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
