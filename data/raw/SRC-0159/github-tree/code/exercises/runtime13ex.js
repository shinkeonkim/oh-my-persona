// 12장 런타임. runtime10ex.js 에 타이머와 비동기 요청, 애니메이션 프레임을 더한다.

// 10장 런타임. runtime9ex.js 에 XMLHttpRequest 와 document.cookie 를 더한다.

// 9장 연습문제용 자바스크립트 런타임.
// runtime9.js 를 넓혀 children / createElement / removeChild / 버블링 /
// innerHTML 읽기 / id 전역 변수를 지원한다.

console = { log: function(x) { call_python("log", x); } }

document = {
    querySelectorAll: function(s) {
        var handles = call_python("querySelectorAll", s);
        return handles.map(function(h) { return new Node(h) });
    },
    // 연습문제 9-2
    createElement: function(tag) {
        return new Node(call_python("createElement", tag));
    },
    createTextNode: function(text) {
        return new Node(call_python("createTextNode", text));
    }
}

function Node(handle) { this.handle = handle; }

// 같은 노드를 가리키는 Node 는 서로 같다고 본다
Node.prototype.isSameNode = function(other) {
    return other && this.handle === other.handle;
}

Node.prototype.getAttribute = function(attr) {
    return call_python("getAttribute", this.handle, attr);
}

Node.prototype.setAttribute = function(attr, value) {
    return call_python("setAttribute", this.handle, attr, value.toString());
}

// 연습문제 9-1: 직계 Element 자식만
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

// 연습문제 9-2
Node.prototype.appendChild = function(child) {
    call_python("appendChild", this.handle, child.handle);
    return child;
}

Node.prototype.insertBefore = function(child, reference) {
    call_python("insertBefore", this.handle, child.handle,
                reference ? reference.handle : -1);
    return child;
}

// 연습문제 9-3
Node.prototype.removeChild = function(child) {
    call_python("removeChild", this.handle, child.handle);
    return child;
}

// 연습문제 9-6: 읽기도 된다
Object.defineProperty(Node.prototype, 'innerHTML', {
    get: function() {
        return call_python("innerHTML_get", this.handle);
    },
    set: function(s) {
        call_python("innerHTML_set", this.handle, s.toString());
    }
});

Object.defineProperty(Node.prototype, 'outerHTML', {
    get: function() {
        return call_python("outerHTML_get", this.handle);
    }
});

LISTENERS = {}

function Event(type) {
    this.type = type;
    this.do_default = true;
    this.cancel_bubble = false;
    this.target = null;
    this.currentTarget = null;
}

Event.prototype.preventDefault = function() {
    this.do_default = false;
}

// 연습문제 9-5
Event.prototype.stopPropagation = function() {
    this.cancel_bubble = true;
}

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

// 연습문제 9-5: 대상에서 시작해 조상으로 거슬러 올라간다
function __dispatch(handles, type) {
    var evt = new Event(type);
    evt.target = new Node(handles[0]);
    for (var i = 0; i < handles.length; i++) {
        var node = new Node(handles[i]);
        evt.currentTarget = node;
        var dict = LISTENERS[handles[i]];
        var list = (dict && dict[type]) || [];
        for (var j = 0; j < list.length; j++) {
            list[j].call(node, evt);
        }
        if (evt.cancel_bubble) break;
    }
    return evt.do_default;
}

Node.prototype.dispatchEvent = function(evt) {
    var handles = call_python("ancestors", this.handle);
    return __dispatch(handles, evt.type);
}

// --- 10장 ---------------------------------------------------------- //

function XMLHttpRequest() {
    this.status = 200;
    this.responseText = "";
}

XMLHttpRequest.prototype.open = function(method, url, is_async) {
    if (is_async) throw Error("비동기 요청은 아직 지원하지 않습니다");
    this.method = method;
    this.url = url;
}

XMLHttpRequest.prototype.send = function(body) {
    this.responseText = call_python("XMLHttpRequest_send",
                                    this.method, this.url, body || "");
}

// 연습문제 10-3
Object.defineProperty(document, 'cookie', {
    get: function() { return call_python("cookie_get"); },
    set: function(s) { call_python("cookie_set", s.toString()); }
});

// --- 12장 ---------------------------------------------------------- //

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

// 연습문제 12-1
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
    if (!callback) return false;     // 이미 취소됐다
    callback();
    // 취소는 콜백 안에서도 일어날 수 있다
    return SET_INTERVAL_REQUESTS[handle] ? true : false;
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

function requestAnimationFrame(fn) {
    RAF_LISTENERS.push(fn);
    call_python("requestAnimationFrame");
}

function __runRAFHandlers() {
    var handlers = RAF_LISTENERS;
    RAF_LISTENERS = [];
    for (var i = 0; i < handlers.length; i++) handlers[i]();
}

// --- 13장 ---------------------------------------------------------- //

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
