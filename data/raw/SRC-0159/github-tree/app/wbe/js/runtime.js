// 브라우저가 페이지 스크립트보다 먼저 돌려 두는 자바스크립트.
//
// 파이썬 쪽 함수는 call_python(이름, ...) 으로 부른다. DOM 노드는 핸들
// (정수) 로 오가고, 이쪽에서는 Node 로 감싼다.

console = { log: function(x) { call_python("log", x); } }

document = {
    querySelectorAll: function(s) {
        var handles = call_python("querySelectorAll", s);
        return handles.map(function(h) { return new Node(h) });
    },
    createElement: function(tag) {
        return new Node(call_python("createElement", tag));
    },
    createTextNode: function(text) {
        return new Node(call_python("createTextNode", text));
    }
}

function Node(handle) { this.handle = handle; }

Node.prototype.isSameNode = function(other) {
    return other && this.handle === other.handle;
}

// --- 속성 ---------------------------------------------------------- //

Node.prototype.getAttribute = function(attr) {
    return call_python("getAttribute", this.handle, attr);
}

Node.prototype.setAttribute = function(attr, value) {
    return call_python("setAttribute", this.handle, attr, value.toString());
}

Object.defineProperty(Node.prototype, 'style', {
    get: function() {
        var handle = this.handle;
        return {
            setProperty: function(prop, value) {
                call_python("style_set_property", handle, prop,
                            value.toString());
            },
            get cssText() { return call_python("style_get", handle); },
            set cssText(s) { call_python("style_set", handle, s.toString()); }
        };
    },
    set: function(s) { call_python("style_set", this.handle, s.toString()); }
});

// --- 트리 ---------------------------------------------------------- //

Object.defineProperty(Node.prototype, 'children', {
    get: function() {
        var handles = call_python("getChildren", this.handle);
        return handles.map(function(h) { return new Node(h) });
    }
});

Object.defineProperty(Node.prototype, 'parentNode', {
    get: function() {
        var h = call_python("getParent", this.handle);
        return h < 0 ? null : new Node(h);
    }
});

Node.prototype.appendChild = function(child) {
    call_python("appendChild", this.handle, child.handle);
    return child;
}

Node.prototype.insertBefore = function(child, reference) {
    call_python("insertBefore", this.handle, child.handle,
                reference ? reference.handle : -1);
    return child;
}

Node.prototype.removeChild = function(child) {
    call_python("removeChild", this.handle, child.handle);
    return child;
}

Node.prototype.replaceChildren = function() {
    var handles = [];
    for (var i = 0; i < arguments.length; i++)
        handles.push(arguments[i].handle);
    call_python("replaceChildren", this.handle, handles);
    return undefined;
}

Object.defineProperty(Node.prototype, 'innerHTML', {
    get: function() { return call_python("innerHTML_get", this.handle); },
    set: function(s) { call_python("innerHTML_set", this.handle, s.toString()); }
});

Object.defineProperty(Node.prototype, 'outerHTML', {
    get: function() { return call_python("outerHTML_get", this.handle); }
});

// --- 포커스 --------------------------------------------------------- //

Node.prototype.focus = function() { call_python("focus", this.handle); }
Node.prototype.blur = function() { call_python("blur_element", this.handle); }

// --- 이벤트 --------------------------------------------------------- //

LISTENERS = {}

function Event(type) {
    this.type = type;
    this.do_default = true;
    this.cancel_bubble = false;
    this.target = null;
    this.currentTarget = null;
}

Event.prototype.preventDefault = function() { this.do_default = false; }
Event.prototype.stopPropagation = function() { this.cancel_bubble = true; }

Node.prototype.addEventListener = function(type, listener) {
    if (!LISTENERS[this.handle]) LISTENERS[this.handle] = {};
    var dict = LISTENERS[this.handle];
    if (!dict[type]) dict[type] = [];
    dict[type].push(listener);
}

Node.prototype.removeEventListener = function(type, listener) {
    var dict = LISTENERS[this.handle];
    if (!dict || !dict[type]) return;
    var list = dict[type];
    for (var i = 0; i < list.length; i++) {
        if (list[i] === listener) { list.splice(i, 1); return; }
    }
}

// 대상에서 조상으로 거슬러 올라간다. 파이썬이 사슬을 만들어 준다.
function __dispatch(handles, type) {
    var evt = new Event(type);
    evt.target = new Node(handles[0]);
    for (var i = 0; i < handles.length; i++) {
        var node = new Node(handles[i]);
        evt.currentTarget = node;
        var dict = LISTENERS[handles[i]];
        var list = (dict && dict[type]) || [];
        for (var j = 0; j < list.length; j++) list[j].call(node, evt);
        if (evt.cancel_bubble) break;
    }
    return evt.do_default;
}

Node.prototype.dispatchEvent = function(evt) {
    return __dispatch(call_python("ancestors", this.handle), evt.type);
}

// --- 타이머 --------------------------------------------------------- //

SET_TIMEOUT_REQUESTS = {}
SET_INTERVAL_REQUESTS = {}
XHR_REQUESTS = {}
RAF_LISTENERS = [];

var __next_handle = 0;
function __new_handle() { return __next_handle++; }

function setTimeout(callback, time_delta) {
    var handle = __new_handle();
    SET_TIMEOUT_REQUESTS[handle] = callback;
    call_python("setTimeout", handle, time_delta);
    return handle;
}

function clearTimeout(handle) {
    delete SET_TIMEOUT_REQUESTS[handle];
    call_python("clearTimeout", handle);
}

function __runSetTimeout(handle) {
    var callback = SET_TIMEOUT_REQUESTS[handle];
    delete SET_TIMEOUT_REQUESTS[handle];
    if (callback) callback();
}

function setInterval(callback, time_delta) {
    var handle = __new_handle();
    SET_INTERVAL_REQUESTS[handle] = callback;
    call_python("setInterval", handle, time_delta);
    return handle;
}

function clearInterval(handle) {
    delete SET_INTERVAL_REQUESTS[handle];
    call_python("clearInterval", handle);
}

function __runSetInterval(handle) {
    var callback = SET_INTERVAL_REQUESTS[handle];
    if (!callback) return false;              // 이미 취소됐다
    callback();
    // 취소는 콜백 안에서도 일어날 수 있다
    return SET_INTERVAL_REQUESTS[handle] ? true : false;
}

function requestAnimationFrame(fn) {
    RAF_LISTENERS.push(fn);
    call_python("requestAnimationFrame");
}

function __runRAFHandlers() {
    var handlers = RAF_LISTENERS;
    RAF_LISTENERS = [];
    for (var i = 0; i < handlers.length; i++) handlers[i]();
}

// --- 네트워크 ------------------------------------------------------- //

function XMLHttpRequest() {
    this.status = 200;
    this.responseText = "";
    this.is_async = true;
}

XMLHttpRequest.prototype.open = function(method, url, is_async) {
    this.is_async = is_async === undefined ? true : is_async;
    this.method = method;
    this.url = url;
}

XMLHttpRequest.prototype.send = function(body) {
    this.handle = __new_handle();
    XHR_REQUESTS[this.handle] = this;
    var out = call_python("XMLHttpRequest_send", this.method, this.url,
                          body || "", this.is_async, this.handle);
    if (!this.is_async) this.responseText = out;
}

function __runXHROnload(body, handle) {
    var obj = XHR_REQUESTS[handle];
    delete XHR_REQUESTS[handle];
    if (!obj) return;
    obj.responseText = body;
    obj.status = 200;
    if (obj.onload) obj.onload();
}

// --- 쿠키 ----------------------------------------------------------- //

Object.defineProperty(document, 'cookie', {
    get: function() { return call_python("cookie_get"); },
    set: function(s) { call_python("cookie_set", s.toString()); }
});

// --- 캔버스 --------------------------------------------------------- //

Node.prototype.getContext = function(type) {
    if (type !== "2d") return null;
    var handle = this.handle;
    return {
        set fillStyle(color) {
            call_python("canvas_fill_style", handle, color.toString());
        },
        fillRect: function(x, y, w, h) {
            call_python("canvas_fill_rect", handle, x, y, w, h);
        },
        fillText: function(text, x, y) {
            call_python("canvas_fill_text", handle, text.toString(), x, y);
        },
        clearRect: function(x, y, w, h) {
            call_python("canvas_clear", handle);
        }
    };
}

// --- 프레임 사이의 메시지 -------------------------------------------- //

window = { parent: null };

function postMessage(message, targetOrigin) {
    call_python("post_message", message.toString(),
                targetOrigin === undefined ? "*" : targetOrigin.toString());
}

WINDOW_LISTENERS = {}

window.addEventListener = function(type, listener) {
    if (!WINDOW_LISTENERS[type]) WINDOW_LISTENERS[type] = [];
    WINDOW_LISTENERS[type].push(listener);
}
window.postMessage = postMessage;

function __runWindowMessage(data, origin) {
    var list = WINDOW_LISTENERS["message"] || [];
    var evt = { data: data, origin: origin };
    for (var i = 0; i < list.length; i++) list[i](evt);
    return list.length;
}
