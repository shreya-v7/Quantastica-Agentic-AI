import Lt, { useState as wt, useEffect as Ur } from "react";
var qe = { exports: {} }, ie = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Rt;
function Br() {
  if (Rt) return ie;
  Rt = 1;
  var e = Lt, t = Symbol.for("react.element"), r = Symbol.for("react.fragment"), n = Object.prototype.hasOwnProperty, s = e.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, i = { key: !0, ref: !0, __self: !0, __source: !0 };
  function a(u, p, d) {
    var l, m = {}, S = null, x = null;
    d !== void 0 && (S = "" + d), p.key !== void 0 && (S = "" + p.key), p.ref !== void 0 && (x = p.ref);
    for (l in p) n.call(p, l) && !i.hasOwnProperty(l) && (m[l] = p[l]);
    if (u && u.defaultProps) for (l in p = u.defaultProps, p) m[l] === void 0 && (m[l] = p[l]);
    return { $$typeof: t, type: u, key: S, ref: x, props: m, _owner: s.current };
  }
  return ie.Fragment = r, ie.jsx = a, ie.jsxs = a, ie;
}
var ae = {};
/**
 * @license React
 * react-jsx-runtime.development.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var St;
function Ir() {
  return St || (St = 1, process.env.NODE_ENV !== "production" && function() {
    var e = Lt, t = Symbol.for("react.element"), r = Symbol.for("react.portal"), n = Symbol.for("react.fragment"), s = Symbol.for("react.strict_mode"), i = Symbol.for("react.profiler"), a = Symbol.for("react.provider"), u = Symbol.for("react.context"), p = Symbol.for("react.forward_ref"), d = Symbol.for("react.suspense"), l = Symbol.for("react.suspense_list"), m = Symbol.for("react.memo"), S = Symbol.for("react.lazy"), x = Symbol.for("react.offscreen"), y = Symbol.iterator, g = "@@iterator";
    function b(o) {
      if (o === null || typeof o != "object")
        return null;
      var f = y && o[y] || o[g];
      return typeof f == "function" ? f : null;
    }
    var _ = e.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED;
    function O(o) {
      {
        for (var f = arguments.length, h = new Array(f > 1 ? f - 1 : 0), E = 1; E < f; E++)
          h[E - 1] = arguments[E];
        F("error", o, h);
      }
    }
    function F(o, f, h) {
      {
        var E = _.ReactDebugCurrentFrame, v = E.getStackAddendum();
        v !== "" && (f += "%s", h = h.concat([v]));
        var A = h.map(function(T) {
          return String(T);
        });
        A.unshift("Warning: " + f), Function.prototype.apply.call(console[o], console, A);
      }
    }
    var q = !1, k = !1, $ = !1, W = !1, Z = !1, ne;
    ne = Symbol.for("react.module.reference");
    function cr(o) {
      return !!(typeof o == "string" || typeof o == "function" || o === n || o === i || Z || o === s || o === d || o === l || W || o === x || q || k || $ || typeof o == "object" && o !== null && (o.$$typeof === S || o.$$typeof === m || o.$$typeof === a || o.$$typeof === u || o.$$typeof === p || // This needs to include all possible module reference object
      // types supported by any Flight configuration anywhere since
      // we don't know which Flight build this will end up being used
      // with.
      o.$$typeof === ne || o.getModuleId !== void 0));
    }
    function ur(o, f, h) {
      var E = o.displayName;
      if (E)
        return E;
      var v = f.displayName || f.name || "";
      return v !== "" ? h + "(" + v + ")" : h;
    }
    function Xe(o) {
      return o.displayName || "Context";
    }
    function z(o) {
      if (o == null)
        return null;
      if (typeof o.tag == "number" && O("Received an unexpected object in getComponentNameFromType(). This is likely a bug in React. Please file an issue."), typeof o == "function")
        return o.displayName || o.name || null;
      if (typeof o == "string")
        return o;
      switch (o) {
        case n:
          return "Fragment";
        case r:
          return "Portal";
        case i:
          return "Profiler";
        case s:
          return "StrictMode";
        case d:
          return "Suspense";
        case l:
          return "SuspenseList";
      }
      if (typeof o == "object")
        switch (o.$$typeof) {
          case u:
            var f = o;
            return Xe(f) + ".Consumer";
          case a:
            var h = o;
            return Xe(h._context) + ".Provider";
          case p:
            return ur(o, o.render, "ForwardRef");
          case m:
            var E = o.displayName || null;
            return E !== null ? E : z(o.type) || "Memo";
          case S: {
            var v = o, A = v._payload, T = v._init;
            try {
              return z(T(A));
            } catch {
              return null;
            }
          }
        }
      return null;
    }
    var J = Object.assign, se = 0, Ge, Ze, Qe, et, tt, rt, nt;
    function st() {
    }
    st.__reactDisabledLog = !0;
    function lr() {
      {
        if (se === 0) {
          Ge = console.log, Ze = console.info, Qe = console.warn, et = console.error, tt = console.group, rt = console.groupCollapsed, nt = console.groupEnd;
          var o = {
            configurable: !0,
            enumerable: !0,
            value: st,
            writable: !0
          };
          Object.defineProperties(console, {
            info: o,
            log: o,
            warn: o,
            error: o,
            group: o,
            groupCollapsed: o,
            groupEnd: o
          });
        }
        se++;
      }
    }
    function fr() {
      {
        if (se--, se === 0) {
          var o = {
            configurable: !0,
            enumerable: !0,
            writable: !0
          };
          Object.defineProperties(console, {
            log: J({}, o, {
              value: Ge
            }),
            info: J({}, o, {
              value: Ze
            }),
            warn: J({}, o, {
              value: Qe
            }),
            error: J({}, o, {
              value: et
            }),
            group: J({}, o, {
              value: tt
            }),
            groupCollapsed: J({}, o, {
              value: rt
            }),
            groupEnd: J({}, o, {
              value: nt
            })
          });
        }
        se < 0 && O("disabledDepth fell below zero. This is a bug in React. Please file an issue.");
      }
    }
    var Ce = _.ReactCurrentDispatcher, Pe;
    function he(o, f, h) {
      {
        if (Pe === void 0)
          try {
            throw Error();
          } catch (v) {
            var E = v.stack.trim().match(/\n( *(at )?)/);
            Pe = E && E[1] || "";
          }
        return `
` + Pe + o;
      }
    }
    var Fe = !1, me;
    {
      var dr = typeof WeakMap == "function" ? WeakMap : Map;
      me = new dr();
    }
    function ot(o, f) {
      if (!o || Fe)
        return "";
      {
        var h = me.get(o);
        if (h !== void 0)
          return h;
      }
      var E;
      Fe = !0;
      var v = Error.prepareStackTrace;
      Error.prepareStackTrace = void 0;
      var A;
      A = Ce.current, Ce.current = null, lr();
      try {
        if (f) {
          var T = function() {
            throw Error();
          };
          if (Object.defineProperty(T.prototype, "props", {
            set: function() {
              throw Error();
            }
          }), typeof Reflect == "object" && Reflect.construct) {
            try {
              Reflect.construct(T, []);
            } catch (L) {
              E = L;
            }
            Reflect.construct(o, [], T);
          } else {
            try {
              T.call();
            } catch (L) {
              E = L;
            }
            o.call(T.prototype);
          }
        } else {
          try {
            throw Error();
          } catch (L) {
            E = L;
          }
          o();
        }
      } catch (L) {
        if (L && E && typeof L.stack == "string") {
          for (var R = L.stack.split(`
`), D = E.stack.split(`
`), C = R.length - 1, j = D.length - 1; C >= 1 && j >= 0 && R[C] !== D[j]; )
            j--;
          for (; C >= 1 && j >= 0; C--, j--)
            if (R[C] !== D[j]) {
              if (C !== 1 || j !== 1)
                do
                  if (C--, j--, j < 0 || R[C] !== D[j]) {
                    var I = `
` + R[C].replace(" at new ", " at ");
                    return o.displayName && I.includes("<anonymous>") && (I = I.replace("<anonymous>", o.displayName)), typeof o == "function" && me.set(o, I), I;
                  }
                while (C >= 1 && j >= 0);
              break;
            }
        }
      } finally {
        Fe = !1, Ce.current = A, fr(), Error.prepareStackTrace = v;
      }
      var ee = o ? o.displayName || o.name : "", K = ee ? he(ee) : "";
      return typeof o == "function" && me.set(o, K), K;
    }
    function pr(o, f, h) {
      return ot(o, !1);
    }
    function hr(o) {
      var f = o.prototype;
      return !!(f && f.isReactComponent);
    }
    function ye(o, f, h) {
      if (o == null)
        return "";
      if (typeof o == "function")
        return ot(o, hr(o));
      if (typeof o == "string")
        return he(o);
      switch (o) {
        case d:
          return he("Suspense");
        case l:
          return he("SuspenseList");
      }
      if (typeof o == "object")
        switch (o.$$typeof) {
          case p:
            return pr(o.render);
          case m:
            return ye(o.type, f, h);
          case S: {
            var E = o, v = E._payload, A = E._init;
            try {
              return ye(A(v), f, h);
            } catch {
            }
          }
        }
      return "";
    }
    var oe = Object.prototype.hasOwnProperty, it = {}, at = _.ReactDebugCurrentFrame;
    function be(o) {
      if (o) {
        var f = o._owner, h = ye(o.type, o._source, f ? f.type : null);
        at.setExtraStackFrame(h);
      } else
        at.setExtraStackFrame(null);
    }
    function mr(o, f, h, E, v) {
      {
        var A = Function.call.bind(oe);
        for (var T in o)
          if (A(o, T)) {
            var R = void 0;
            try {
              if (typeof o[T] != "function") {
                var D = Error((E || "React class") + ": " + h + " type `" + T + "` is invalid; it must be a function, usually from the `prop-types` package, but received `" + typeof o[T] + "`.This often happens because of typos such as `PropTypes.function` instead of `PropTypes.func`.");
                throw D.name = "Invariant Violation", D;
              }
              R = o[T](f, T, E, h, null, "SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED");
            } catch (C) {
              R = C;
            }
            R && !(R instanceof Error) && (be(v), O("%s: type specification of %s `%s` is invalid; the type checker function must return `null` or an `Error` but returned a %s. You may have forgotten to pass an argument to the type checker creator (arrayOf, instanceOf, objectOf, oneOf, oneOfType, and shape all require an argument).", E || "React class", h, T, typeof R), be(null)), R instanceof Error && !(R.message in it) && (it[R.message] = !0, be(v), O("Failed %s type: %s", h, R.message), be(null));
          }
      }
    }
    var yr = Array.isArray;
    function je(o) {
      return yr(o);
    }
    function br(o) {
      {
        var f = typeof Symbol == "function" && Symbol.toStringTag, h = f && o[Symbol.toStringTag] || o.constructor.name || "Object";
        return h;
      }
    }
    function Er(o) {
      try {
        return ct(o), !1;
      } catch {
        return !0;
      }
    }
    function ct(o) {
      return "" + o;
    }
    function ut(o) {
      if (Er(o))
        return O("The provided key is an unsupported type %s. This value must be coerced to a string before before using it here.", br(o)), ct(o);
    }
    var lt = _.ReactCurrentOwner, gr = {
      key: !0,
      ref: !0,
      __self: !0,
      __source: !0
    }, ft, dt;
    function wr(o) {
      if (oe.call(o, "ref")) {
        var f = Object.getOwnPropertyDescriptor(o, "ref").get;
        if (f && f.isReactWarning)
          return !1;
      }
      return o.ref !== void 0;
    }
    function Rr(o) {
      if (oe.call(o, "key")) {
        var f = Object.getOwnPropertyDescriptor(o, "key").get;
        if (f && f.isReactWarning)
          return !1;
      }
      return o.key !== void 0;
    }
    function Sr(o, f) {
      typeof o.ref == "string" && lt.current;
    }
    function Or(o, f) {
      {
        var h = function() {
          ft || (ft = !0, O("%s: `key` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://reactjs.org/link/special-props)", f));
        };
        h.isReactWarning = !0, Object.defineProperty(o, "key", {
          get: h,
          configurable: !0
        });
      }
    }
    function Tr(o, f) {
      {
        var h = function() {
          dt || (dt = !0, O("%s: `ref` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://reactjs.org/link/special-props)", f));
        };
        h.isReactWarning = !0, Object.defineProperty(o, "ref", {
          get: h,
          configurable: !0
        });
      }
    }
    var vr = function(o, f, h, E, v, A, T) {
      var R = {
        // This tag allows us to uniquely identify this as a React Element
        $$typeof: t,
        // Built-in properties that belong on the element
        type: o,
        key: f,
        ref: h,
        props: T,
        // Record the component responsible for creating this element.
        _owner: A
      };
      return R._store = {}, Object.defineProperty(R._store, "validated", {
        configurable: !1,
        enumerable: !1,
        writable: !0,
        value: !1
      }), Object.defineProperty(R, "_self", {
        configurable: !1,
        enumerable: !1,
        writable: !1,
        value: E
      }), Object.defineProperty(R, "_source", {
        configurable: !1,
        enumerable: !1,
        writable: !1,
        value: v
      }), Object.freeze && (Object.freeze(R.props), Object.freeze(R)), R;
    };
    function _r(o, f, h, E, v) {
      {
        var A, T = {}, R = null, D = null;
        h !== void 0 && (ut(h), R = "" + h), Rr(f) && (ut(f.key), R = "" + f.key), wr(f) && (D = f.ref, Sr(f, v));
        for (A in f)
          oe.call(f, A) && !gr.hasOwnProperty(A) && (T[A] = f[A]);
        if (o && o.defaultProps) {
          var C = o.defaultProps;
          for (A in C)
            T[A] === void 0 && (T[A] = C[A]);
        }
        if (R || D) {
          var j = typeof o == "function" ? o.displayName || o.name || "Unknown" : o;
          R && Or(T, j), D && Tr(T, j);
        }
        return vr(o, R, D, v, E, lt.current, T);
      }
    }
    var ke = _.ReactCurrentOwner, pt = _.ReactDebugCurrentFrame;
    function Q(o) {
      if (o) {
        var f = o._owner, h = ye(o.type, o._source, f ? f.type : null);
        pt.setExtraStackFrame(h);
      } else
        pt.setExtraStackFrame(null);
    }
    var Ne;
    Ne = !1;
    function De(o) {
      return typeof o == "object" && o !== null && o.$$typeof === t;
    }
    function ht() {
      {
        if (ke.current) {
          var o = z(ke.current.type);
          if (o)
            return `

Check the render method of \`` + o + "`.";
        }
        return "";
      }
    }
    function Ar(o) {
      return "";
    }
    var mt = {};
    function xr(o) {
      {
        var f = ht();
        if (!f) {
          var h = typeof o == "string" ? o : o.displayName || o.name;
          h && (f = `

Check the top-level render call using <` + h + ">.");
        }
        return f;
      }
    }
    function yt(o, f) {
      {
        if (!o._store || o._store.validated || o.key != null)
          return;
        o._store.validated = !0;
        var h = xr(f);
        if (mt[h])
          return;
        mt[h] = !0;
        var E = "";
        o && o._owner && o._owner !== ke.current && (E = " It was passed a child from " + z(o._owner.type) + "."), Q(o), O('Each child in a list should have a unique "key" prop.%s%s See https://reactjs.org/link/warning-keys for more information.', h, E), Q(null);
      }
    }
    function bt(o, f) {
      {
        if (typeof o != "object")
          return;
        if (je(o))
          for (var h = 0; h < o.length; h++) {
            var E = o[h];
            De(E) && yt(E, f);
          }
        else if (De(o))
          o._store && (o._store.validated = !0);
        else if (o) {
          var v = b(o);
          if (typeof v == "function" && v !== o.entries)
            for (var A = v.call(o), T; !(T = A.next()).done; )
              De(T.value) && yt(T.value, f);
        }
      }
    }
    function Cr(o) {
      {
        var f = o.type;
        if (f == null || typeof f == "string")
          return;
        var h;
        if (typeof f == "function")
          h = f.propTypes;
        else if (typeof f == "object" && (f.$$typeof === p || // Note: Memo only checks outer props here.
        // Inner props are checked in the reconciler.
        f.$$typeof === m))
          h = f.propTypes;
        else
          return;
        if (h) {
          var E = z(f);
          mr(h, o.props, "prop", E, o);
        } else if (f.PropTypes !== void 0 && !Ne) {
          Ne = !0;
          var v = z(f);
          O("Component %s declared `PropTypes` instead of `propTypes`. Did you misspell the property assignment?", v || "Unknown");
        }
        typeof f.getDefaultProps == "function" && !f.getDefaultProps.isReactClassApproved && O("getDefaultProps is only used on classic React.createClass definitions. Use a static property named `defaultProps` instead.");
      }
    }
    function Pr(o) {
      {
        for (var f = Object.keys(o.props), h = 0; h < f.length; h++) {
          var E = f[h];
          if (E !== "children" && E !== "key") {
            Q(o), O("Invalid prop `%s` supplied to `React.Fragment`. React.Fragment can only have `key` and `children` props.", E), Q(null);
            break;
          }
        }
        o.ref !== null && (Q(o), O("Invalid attribute `ref` supplied to `React.Fragment`."), Q(null));
      }
    }
    var Et = {};
    function gt(o, f, h, E, v, A) {
      {
        var T = cr(o);
        if (!T) {
          var R = "";
          (o === void 0 || typeof o == "object" && o !== null && Object.keys(o).length === 0) && (R += " You likely forgot to export your component from the file it's defined in, or you might have mixed up default and named imports.");
          var D = Ar();
          D ? R += D : R += ht();
          var C;
          o === null ? C = "null" : je(o) ? C = "array" : o !== void 0 && o.$$typeof === t ? (C = "<" + (z(o.type) || "Unknown") + " />", R = " Did you accidentally export a JSX literal instead of a component?") : C = typeof o, O("React.jsx: type is invalid -- expected a string (for built-in components) or a class/function (for composite components) but got: %s.%s", C, R);
        }
        var j = _r(o, f, h, v, A);
        if (j == null)
          return j;
        if (T) {
          var I = f.children;
          if (I !== void 0)
            if (E)
              if (je(I)) {
                for (var ee = 0; ee < I.length; ee++)
                  bt(I[ee], o);
                Object.freeze && Object.freeze(I);
              } else
                O("React.jsx: Static children should always be an array. You are likely explicitly calling React.jsxs or React.jsxDEV. Use the Babel transform instead.");
            else
              bt(I, o);
        }
        if (oe.call(f, "key")) {
          var K = z(o), L = Object.keys(f).filter(function(Lr) {
            return Lr !== "key";
          }), Le = L.length > 0 ? "{key: someKey, " + L.join(": ..., ") + ": ...}" : "{key: someKey}";
          if (!Et[K + Le]) {
            var Dr = L.length > 0 ? "{" + L.join(": ..., ") + ": ...}" : "{}";
            O(`A props object containing a "key" prop is being spread into JSX:
  let props = %s;
  <%s {...props} />
React keys must be passed directly to JSX without using spread:
  let props = %s;
  <%s key={someKey} {...props} />`, Le, K, Dr, K), Et[K + Le] = !0;
          }
        }
        return o === n ? Pr(j) : Cr(j), j;
      }
    }
    function Fr(o, f, h) {
      return gt(o, f, h, !0);
    }
    function jr(o, f, h) {
      return gt(o, f, h, !1);
    }
    var kr = jr, Nr = Fr;
    ae.Fragment = n, ae.jsx = kr, ae.jsxs = Nr;
  }()), ae;
}
process.env.NODE_ENV === "production" ? qe.exports = Br() : qe.exports = Ir();
var V = qe.exports;
function Ut(e, t) {
  return function() {
    return e.apply(t, arguments);
  };
}
const { toString: qr } = Object.prototype, { getPrototypeOf: Je } = Object, { iterator: Oe, toStringTag: Bt } = Symbol, Te = /* @__PURE__ */ ((e) => (t) => {
  const r = qr.call(t);
  return e[r] || (e[r] = r.slice(8, -1).toLowerCase());
})(/* @__PURE__ */ Object.create(null)), M = (e) => (e = e.toLowerCase(), (t) => Te(t) === e), ve = (e) => (t) => typeof t === e, { isArray: te } = Array, ue = ve("undefined");
function le(e) {
  return e !== null && !ue(e) && e.constructor !== null && !ue(e.constructor) && U(e.constructor.isBuffer) && e.constructor.isBuffer(e);
}
const It = M("ArrayBuffer");
function Mr(e) {
  let t;
  return typeof ArrayBuffer < "u" && ArrayBuffer.isView ? t = ArrayBuffer.isView(e) : t = e && e.buffer && It(e.buffer), t;
}
const $r = ve("string"), U = ve("function"), qt = ve("number"), fe = (e) => e !== null && typeof e == "object", Hr = (e) => e === !0 || e === !1, Ee = (e) => {
  if (Te(e) !== "object")
    return !1;
  const t = Je(e);
  return (t === null || t === Object.prototype || Object.getPrototypeOf(t) === null) && !(Bt in e) && !(Oe in e);
}, Wr = (e) => {
  if (!fe(e) || le(e))
    return !1;
  try {
    return Object.keys(e).length === 0 && Object.getPrototypeOf(e) === Object.prototype;
  } catch {
    return !1;
  }
}, Vr = M("Date"), zr = M("File"), Jr = M("Blob"), Kr = M("FileList"), Yr = (e) => fe(e) && U(e.pipe), Xr = (e) => {
  let t;
  return e && (typeof FormData == "function" && e instanceof FormData || U(e.append) && ((t = Te(e)) === "formdata" || // detect form-data instance
  t === "object" && U(e.toString) && e.toString() === "[object FormData]"));
}, Gr = M("URLSearchParams"), [Zr, Qr, en, tn] = ["ReadableStream", "Request", "Response", "Headers"].map(M), rn = (e) => e.trim ? e.trim() : e.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g, "");
function de(e, t, { allOwnKeys: r = !1 } = {}) {
  if (e === null || typeof e > "u")
    return;
  let n, s;
  if (typeof e != "object" && (e = [e]), te(e))
    for (n = 0, s = e.length; n < s; n++)
      t.call(null, e[n], n, e);
  else {
    if (le(e))
      return;
    const i = r ? Object.getOwnPropertyNames(e) : Object.keys(e), a = i.length;
    let u;
    for (n = 0; n < a; n++)
      u = i[n], t.call(null, e[u], u, e);
  }
}
function Mt(e, t) {
  if (le(e))
    return null;
  t = t.toLowerCase();
  const r = Object.keys(e);
  let n = r.length, s;
  for (; n-- > 0; )
    if (s = r[n], t === s.toLowerCase())
      return s;
  return null;
}
const Y = typeof globalThis < "u" ? globalThis : typeof self < "u" ? self : typeof window < "u" ? window : global, $t = (e) => !ue(e) && e !== Y;
function Me() {
  const { caseless: e } = $t(this) && this || {}, t = {}, r = (n, s) => {
    const i = e && Mt(t, s) || s;
    Ee(t[i]) && Ee(n) ? t[i] = Me(t[i], n) : Ee(n) ? t[i] = Me({}, n) : te(n) ? t[i] = n.slice() : t[i] = n;
  };
  for (let n = 0, s = arguments.length; n < s; n++)
    arguments[n] && de(arguments[n], r);
  return t;
}
const nn = (e, t, r, { allOwnKeys: n } = {}) => (de(t, (s, i) => {
  r && U(s) ? e[i] = Ut(s, r) : e[i] = s;
}, { allOwnKeys: n }), e), sn = (e) => (e.charCodeAt(0) === 65279 && (e = e.slice(1)), e), on = (e, t, r, n) => {
  e.prototype = Object.create(t.prototype, n), e.prototype.constructor = e, Object.defineProperty(e, "super", {
    value: t.prototype
  }), r && Object.assign(e.prototype, r);
}, an = (e, t, r, n) => {
  let s, i, a;
  const u = {};
  if (t = t || {}, e == null) return t;
  do {
    for (s = Object.getOwnPropertyNames(e), i = s.length; i-- > 0; )
      a = s[i], (!n || n(a, e, t)) && !u[a] && (t[a] = e[a], u[a] = !0);
    e = r !== !1 && Je(e);
  } while (e && (!r || r(e, t)) && e !== Object.prototype);
  return t;
}, cn = (e, t, r) => {
  e = String(e), (r === void 0 || r > e.length) && (r = e.length), r -= t.length;
  const n = e.indexOf(t, r);
  return n !== -1 && n === r;
}, un = (e) => {
  if (!e) return null;
  if (te(e)) return e;
  let t = e.length;
  if (!qt(t)) return null;
  const r = new Array(t);
  for (; t-- > 0; )
    r[t] = e[t];
  return r;
}, ln = /* @__PURE__ */ ((e) => (t) => e && t instanceof e)(typeof Uint8Array < "u" && Je(Uint8Array)), fn = (e, t) => {
  const n = (e && e[Oe]).call(e);
  let s;
  for (; (s = n.next()) && !s.done; ) {
    const i = s.value;
    t.call(e, i[0], i[1]);
  }
}, dn = (e, t) => {
  let r;
  const n = [];
  for (; (r = e.exec(t)) !== null; )
    n.push(r);
  return n;
}, pn = M("HTMLFormElement"), hn = (e) => e.toLowerCase().replace(
  /[-_\s]([a-z\d])(\w*)/g,
  function(r, n, s) {
    return n.toUpperCase() + s;
  }
), Ot = (({ hasOwnProperty: e }) => (t, r) => e.call(t, r))(Object.prototype), mn = M("RegExp"), Ht = (e, t) => {
  const r = Object.getOwnPropertyDescriptors(e), n = {};
  de(r, (s, i) => {
    let a;
    (a = t(s, i, e)) !== !1 && (n[i] = a || s);
  }), Object.defineProperties(e, n);
}, yn = (e) => {
  Ht(e, (t, r) => {
    if (U(e) && ["arguments", "caller", "callee"].indexOf(r) !== -1)
      return !1;
    const n = e[r];
    if (U(n)) {
      if (t.enumerable = !1, "writable" in t) {
        t.writable = !1;
        return;
      }
      t.set || (t.set = () => {
        throw Error("Can not rewrite read-only method '" + r + "'");
      });
    }
  });
}, bn = (e, t) => {
  const r = {}, n = (s) => {
    s.forEach((i) => {
      r[i] = !0;
    });
  };
  return te(e) ? n(e) : n(String(e).split(t)), r;
}, En = () => {
}, gn = (e, t) => e != null && Number.isFinite(e = +e) ? e : t;
function wn(e) {
  return !!(e && U(e.append) && e[Bt] === "FormData" && e[Oe]);
}
const Rn = (e) => {
  const t = new Array(10), r = (n, s) => {
    if (fe(n)) {
      if (t.indexOf(n) >= 0)
        return;
      if (le(n))
        return n;
      if (!("toJSON" in n)) {
        t[s] = n;
        const i = te(n) ? [] : {};
        return de(n, (a, u) => {
          const p = r(a, s + 1);
          !ue(p) && (i[u] = p);
        }), t[s] = void 0, i;
      }
    }
    return n;
  };
  return r(e, 0);
}, Sn = M("AsyncFunction"), On = (e) => e && (fe(e) || U(e)) && U(e.then) && U(e.catch), Wt = ((e, t) => e ? setImmediate : t ? ((r, n) => (Y.addEventListener("message", ({ source: s, data: i }) => {
  s === Y && i === r && n.length && n.shift()();
}, !1), (s) => {
  n.push(s), Y.postMessage(r, "*");
}))(`axios@${Math.random()}`, []) : (r) => setTimeout(r))(
  typeof setImmediate == "function",
  U(Y.postMessage)
), Tn = typeof queueMicrotask < "u" ? queueMicrotask.bind(Y) : typeof process < "u" && process.nextTick || Wt, vn = (e) => e != null && U(e[Oe]), c = {
  isArray: te,
  isArrayBuffer: It,
  isBuffer: le,
  isFormData: Xr,
  isArrayBufferView: Mr,
  isString: $r,
  isNumber: qt,
  isBoolean: Hr,
  isObject: fe,
  isPlainObject: Ee,
  isEmptyObject: Wr,
  isReadableStream: Zr,
  isRequest: Qr,
  isResponse: en,
  isHeaders: tn,
  isUndefined: ue,
  isDate: Vr,
  isFile: zr,
  isBlob: Jr,
  isRegExp: mn,
  isFunction: U,
  isStream: Yr,
  isURLSearchParams: Gr,
  isTypedArray: ln,
  isFileList: Kr,
  forEach: de,
  merge: Me,
  extend: nn,
  trim: rn,
  stripBOM: sn,
  inherits: on,
  toFlatObject: an,
  kindOf: Te,
  kindOfTest: M,
  endsWith: cn,
  toArray: un,
  forEachEntry: fn,
  matchAll: dn,
  isHTMLForm: pn,
  hasOwnProperty: Ot,
  hasOwnProp: Ot,
  // an alias to avoid ESLint no-prototype-builtins detection
  reduceDescriptors: Ht,
  freezeMethods: yn,
  toObjectSet: bn,
  toCamelCase: hn,
  noop: En,
  toFiniteNumber: gn,
  findKey: Mt,
  global: Y,
  isContextDefined: $t,
  isSpecCompliantForm: wn,
  toJSONObject: Rn,
  isAsyncFn: Sn,
  isThenable: On,
  setImmediate: Wt,
  asap: Tn,
  isIterable: vn
};
function w(e, t, r, n, s) {
  Error.call(this), Error.captureStackTrace ? Error.captureStackTrace(this, this.constructor) : this.stack = new Error().stack, this.message = e, this.name = "AxiosError", t && (this.code = t), r && (this.config = r), n && (this.request = n), s && (this.response = s, this.status = s.status ? s.status : null);
}
c.inherits(w, Error, {
  toJSON: function() {
    return {
      // Standard
      message: this.message,
      name: this.name,
      // Microsoft
      description: this.description,
      number: this.number,
      // Mozilla
      fileName: this.fileName,
      lineNumber: this.lineNumber,
      columnNumber: this.columnNumber,
      stack: this.stack,
      // Axios
      config: c.toJSONObject(this.config),
      code: this.code,
      status: this.status
    };
  }
});
const Vt = w.prototype, zt = {};
[
  "ERR_BAD_OPTION_VALUE",
  "ERR_BAD_OPTION",
  "ECONNABORTED",
  "ETIMEDOUT",
  "ERR_NETWORK",
  "ERR_FR_TOO_MANY_REDIRECTS",
  "ERR_DEPRECATED",
  "ERR_BAD_RESPONSE",
  "ERR_BAD_REQUEST",
  "ERR_CANCELED",
  "ERR_NOT_SUPPORT",
  "ERR_INVALID_URL"
  // eslint-disable-next-line func-names
].forEach((e) => {
  zt[e] = { value: e };
});
Object.defineProperties(w, zt);
Object.defineProperty(Vt, "isAxiosError", { value: !0 });
w.from = (e, t, r, n, s, i) => {
  const a = Object.create(Vt);
  return c.toFlatObject(e, a, function(p) {
    return p !== Error.prototype;
  }, (u) => u !== "isAxiosError"), w.call(a, e.message, t, r, n, s), a.cause = e, a.name = e.name, i && Object.assign(a, i), a;
};
const _n = null;
function $e(e) {
  return c.isPlainObject(e) || c.isArray(e);
}
function Jt(e) {
  return c.endsWith(e, "[]") ? e.slice(0, -2) : e;
}
function Tt(e, t, r) {
  return e ? e.concat(t).map(function(s, i) {
    return s = Jt(s), !r && i ? "[" + s + "]" : s;
  }).join(r ? "." : "") : t;
}
function An(e) {
  return c.isArray(e) && !e.some($e);
}
const xn = c.toFlatObject(c, {}, null, function(t) {
  return /^is[A-Z]/.test(t);
});
function _e(e, t, r) {
  if (!c.isObject(e))
    throw new TypeError("target must be an object");
  t = t || new FormData(), r = c.toFlatObject(r, {
    metaTokens: !0,
    dots: !1,
    indexes: !1
  }, !1, function(g, b) {
    return !c.isUndefined(b[g]);
  });
  const n = r.metaTokens, s = r.visitor || l, i = r.dots, a = r.indexes, p = (r.Blob || typeof Blob < "u" && Blob) && c.isSpecCompliantForm(t);
  if (!c.isFunction(s))
    throw new TypeError("visitor must be a function");
  function d(y) {
    if (y === null) return "";
    if (c.isDate(y))
      return y.toISOString();
    if (c.isBoolean(y))
      return y.toString();
    if (!p && c.isBlob(y))
      throw new w("Blob is not supported. Use a Buffer instead.");
    return c.isArrayBuffer(y) || c.isTypedArray(y) ? p && typeof Blob == "function" ? new Blob([y]) : Buffer.from(y) : y;
  }
  function l(y, g, b) {
    let _ = y;
    if (y && !b && typeof y == "object") {
      if (c.endsWith(g, "{}"))
        g = n ? g : g.slice(0, -2), y = JSON.stringify(y);
      else if (c.isArray(y) && An(y) || (c.isFileList(y) || c.endsWith(g, "[]")) && (_ = c.toArray(y)))
        return g = Jt(g), _.forEach(function(F, q) {
          !(c.isUndefined(F) || F === null) && t.append(
            // eslint-disable-next-line no-nested-ternary
            a === !0 ? Tt([g], q, i) : a === null ? g : g + "[]",
            d(F)
          );
        }), !1;
    }
    return $e(y) ? !0 : (t.append(Tt(b, g, i), d(y)), !1);
  }
  const m = [], S = Object.assign(xn, {
    defaultVisitor: l,
    convertValue: d,
    isVisitable: $e
  });
  function x(y, g) {
    if (!c.isUndefined(y)) {
      if (m.indexOf(y) !== -1)
        throw Error("Circular reference detected in " + g.join("."));
      m.push(y), c.forEach(y, function(_, O) {
        (!(c.isUndefined(_) || _ === null) && s.call(
          t,
          _,
          c.isString(O) ? O.trim() : O,
          g,
          S
        )) === !0 && x(_, g ? g.concat(O) : [O]);
      }), m.pop();
    }
  }
  if (!c.isObject(e))
    throw new TypeError("data must be an object");
  return x(e), t;
}
function vt(e) {
  const t = {
    "!": "%21",
    "'": "%27",
    "(": "%28",
    ")": "%29",
    "~": "%7E",
    "%20": "+",
    "%00": "\0"
  };
  return encodeURIComponent(e).replace(/[!'()~]|%20|%00/g, function(n) {
    return t[n];
  });
}
function Ke(e, t) {
  this._pairs = [], e && _e(e, this, t);
}
const Kt = Ke.prototype;
Kt.append = function(t, r) {
  this._pairs.push([t, r]);
};
Kt.toString = function(t) {
  const r = t ? function(n) {
    return t.call(this, n, vt);
  } : vt;
  return this._pairs.map(function(s) {
    return r(s[0]) + "=" + r(s[1]);
  }, "").join("&");
};
function Cn(e) {
  return encodeURIComponent(e).replace(/%3A/gi, ":").replace(/%24/g, "$").replace(/%2C/gi, ",").replace(/%20/g, "+").replace(/%5B/gi, "[").replace(/%5D/gi, "]");
}
function Yt(e, t, r) {
  if (!t)
    return e;
  const n = r && r.encode || Cn;
  c.isFunction(r) && (r = {
    serialize: r
  });
  const s = r && r.serialize;
  let i;
  if (s ? i = s(t, r) : i = c.isURLSearchParams(t) ? t.toString() : new Ke(t, r).toString(n), i) {
    const a = e.indexOf("#");
    a !== -1 && (e = e.slice(0, a)), e += (e.indexOf("?") === -1 ? "?" : "&") + i;
  }
  return e;
}
class _t {
  constructor() {
    this.handlers = [];
  }
  /**
   * Add a new interceptor to the stack
   *
   * @param {Function} fulfilled The function to handle `then` for a `Promise`
   * @param {Function} rejected The function to handle `reject` for a `Promise`
   *
   * @return {Number} An ID used to remove interceptor later
   */
  use(t, r, n) {
    return this.handlers.push({
      fulfilled: t,
      rejected: r,
      synchronous: n ? n.synchronous : !1,
      runWhen: n ? n.runWhen : null
    }), this.handlers.length - 1;
  }
  /**
   * Remove an interceptor from the stack
   *
   * @param {Number} id The ID that was returned by `use`
   *
   * @returns {Boolean} `true` if the interceptor was removed, `false` otherwise
   */
  eject(t) {
    this.handlers[t] && (this.handlers[t] = null);
  }
  /**
   * Clear all interceptors from the stack
   *
   * @returns {void}
   */
  clear() {
    this.handlers && (this.handlers = []);
  }
  /**
   * Iterate over all the registered interceptors
   *
   * This method is particularly useful for skipping over any
   * interceptors that may have become `null` calling `eject`.
   *
   * @param {Function} fn The function to call for each interceptor
   *
   * @returns {void}
   */
  forEach(t) {
    c.forEach(this.handlers, function(n) {
      n !== null && t(n);
    });
  }
}
const Xt = {
  silentJSONParsing: !0,
  forcedJSONParsing: !0,
  clarifyTimeoutError: !1
}, Pn = typeof URLSearchParams < "u" ? URLSearchParams : Ke, Fn = typeof FormData < "u" ? FormData : null, jn = typeof Blob < "u" ? Blob : null, kn = {
  isBrowser: !0,
  classes: {
    URLSearchParams: Pn,
    FormData: Fn,
    Blob: jn
  },
  protocols: ["http", "https", "file", "blob", "url", "data"]
}, Ye = typeof window < "u" && typeof document < "u", He = typeof navigator == "object" && navigator || void 0, Nn = Ye && (!He || ["ReactNative", "NativeScript", "NS"].indexOf(He.product) < 0), Dn = typeof WorkerGlobalScope < "u" && // eslint-disable-next-line no-undef
self instanceof WorkerGlobalScope && typeof self.importScripts == "function", Ln = Ye && window.location.href || "http://localhost", Un = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  hasBrowserEnv: Ye,
  hasStandardBrowserEnv: Nn,
  hasStandardBrowserWebWorkerEnv: Dn,
  navigator: He,
  origin: Ln
}, Symbol.toStringTag, { value: "Module" })), N = {
  ...Un,
  ...kn
};
function Bn(e, t) {
  return _e(e, new N.classes.URLSearchParams(), {
    visitor: function(r, n, s, i) {
      return N.isNode && c.isBuffer(r) ? (this.append(n, r.toString("base64")), !1) : i.defaultVisitor.apply(this, arguments);
    },
    ...t
  });
}
function In(e) {
  return c.matchAll(/\w+|\[(\w*)]/g, e).map((t) => t[0] === "[]" ? "" : t[1] || t[0]);
}
function qn(e) {
  const t = {}, r = Object.keys(e);
  let n;
  const s = r.length;
  let i;
  for (n = 0; n < s; n++)
    i = r[n], t[i] = e[i];
  return t;
}
function Gt(e) {
  function t(r, n, s, i) {
    let a = r[i++];
    if (a === "__proto__") return !0;
    const u = Number.isFinite(+a), p = i >= r.length;
    return a = !a && c.isArray(s) ? s.length : a, p ? (c.hasOwnProp(s, a) ? s[a] = [s[a], n] : s[a] = n, !u) : ((!s[a] || !c.isObject(s[a])) && (s[a] = []), t(r, n, s[a], i) && c.isArray(s[a]) && (s[a] = qn(s[a])), !u);
  }
  if (c.isFormData(e) && c.isFunction(e.entries)) {
    const r = {};
    return c.forEachEntry(e, (n, s) => {
      t(In(n), s, r, 0);
    }), r;
  }
  return null;
}
function Mn(e, t, r) {
  if (c.isString(e))
    try {
      return (t || JSON.parse)(e), c.trim(e);
    } catch (n) {
      if (n.name !== "SyntaxError")
        throw n;
    }
  return (r || JSON.stringify)(e);
}
const pe = {
  transitional: Xt,
  adapter: ["xhr", "http", "fetch"],
  transformRequest: [function(t, r) {
    const n = r.getContentType() || "", s = n.indexOf("application/json") > -1, i = c.isObject(t);
    if (i && c.isHTMLForm(t) && (t = new FormData(t)), c.isFormData(t))
      return s ? JSON.stringify(Gt(t)) : t;
    if (c.isArrayBuffer(t) || c.isBuffer(t) || c.isStream(t) || c.isFile(t) || c.isBlob(t) || c.isReadableStream(t))
      return t;
    if (c.isArrayBufferView(t))
      return t.buffer;
    if (c.isURLSearchParams(t))
      return r.setContentType("application/x-www-form-urlencoded;charset=utf-8", !1), t.toString();
    let u;
    if (i) {
      if (n.indexOf("application/x-www-form-urlencoded") > -1)
        return Bn(t, this.formSerializer).toString();
      if ((u = c.isFileList(t)) || n.indexOf("multipart/form-data") > -1) {
        const p = this.env && this.env.FormData;
        return _e(
          u ? { "files[]": t } : t,
          p && new p(),
          this.formSerializer
        );
      }
    }
    return i || s ? (r.setContentType("application/json", !1), Mn(t)) : t;
  }],
  transformResponse: [function(t) {
    const r = this.transitional || pe.transitional, n = r && r.forcedJSONParsing, s = this.responseType === "json";
    if (c.isResponse(t) || c.isReadableStream(t))
      return t;
    if (t && c.isString(t) && (n && !this.responseType || s)) {
      const a = !(r && r.silentJSONParsing) && s;
      try {
        return JSON.parse(t);
      } catch (u) {
        if (a)
          throw u.name === "SyntaxError" ? w.from(u, w.ERR_BAD_RESPONSE, this, null, this.response) : u;
      }
    }
    return t;
  }],
  /**
   * A timeout in milliseconds to abort a request. If set to 0 (default) a
   * timeout is not created.
   */
  timeout: 0,
  xsrfCookieName: "XSRF-TOKEN",
  xsrfHeaderName: "X-XSRF-TOKEN",
  maxContentLength: -1,
  maxBodyLength: -1,
  env: {
    FormData: N.classes.FormData,
    Blob: N.classes.Blob
  },
  validateStatus: function(t) {
    return t >= 200 && t < 300;
  },
  headers: {
    common: {
      Accept: "application/json, text/plain, */*",
      "Content-Type": void 0
    }
  }
};
c.forEach(["delete", "get", "head", "post", "put", "patch"], (e) => {
  pe.headers[e] = {};
});
const $n = c.toObjectSet([
  "age",
  "authorization",
  "content-length",
  "content-type",
  "etag",
  "expires",
  "from",
  "host",
  "if-modified-since",
  "if-unmodified-since",
  "last-modified",
  "location",
  "max-forwards",
  "proxy-authorization",
  "referer",
  "retry-after",
  "user-agent"
]), Hn = (e) => {
  const t = {};
  let r, n, s;
  return e && e.split(`
`).forEach(function(a) {
    s = a.indexOf(":"), r = a.substring(0, s).trim().toLowerCase(), n = a.substring(s + 1).trim(), !(!r || t[r] && $n[r]) && (r === "set-cookie" ? t[r] ? t[r].push(n) : t[r] = [n] : t[r] = t[r] ? t[r] + ", " + n : n);
  }), t;
}, At = Symbol("internals");
function ce(e) {
  return e && String(e).trim().toLowerCase();
}
function ge(e) {
  return e === !1 || e == null ? e : c.isArray(e) ? e.map(ge) : String(e);
}
function Wn(e) {
  const t = /* @__PURE__ */ Object.create(null), r = /([^\s,;=]+)\s*(?:=\s*([^,;]+))?/g;
  let n;
  for (; n = r.exec(e); )
    t[n[1]] = n[2];
  return t;
}
const Vn = (e) => /^[-_a-zA-Z0-9^`|~,!#$%&'*+.]+$/.test(e.trim());
function Ue(e, t, r, n, s) {
  if (c.isFunction(n))
    return n.call(this, t, r);
  if (s && (t = r), !!c.isString(t)) {
    if (c.isString(n))
      return t.indexOf(n) !== -1;
    if (c.isRegExp(n))
      return n.test(t);
  }
}
function zn(e) {
  return e.trim().toLowerCase().replace(/([a-z\d])(\w*)/g, (t, r, n) => r.toUpperCase() + n);
}
function Jn(e, t) {
  const r = c.toCamelCase(" " + t);
  ["get", "set", "has"].forEach((n) => {
    Object.defineProperty(e, n + r, {
      value: function(s, i, a) {
        return this[n].call(this, t, s, i, a);
      },
      configurable: !0
    });
  });
}
let B = class {
  constructor(t) {
    t && this.set(t);
  }
  set(t, r, n) {
    const s = this;
    function i(u, p, d) {
      const l = ce(p);
      if (!l)
        throw new Error("header name must be a non-empty string");
      const m = c.findKey(s, l);
      (!m || s[m] === void 0 || d === !0 || d === void 0 && s[m] !== !1) && (s[m || p] = ge(u));
    }
    const a = (u, p) => c.forEach(u, (d, l) => i(d, l, p));
    if (c.isPlainObject(t) || t instanceof this.constructor)
      a(t, r);
    else if (c.isString(t) && (t = t.trim()) && !Vn(t))
      a(Hn(t), r);
    else if (c.isObject(t) && c.isIterable(t)) {
      let u = {}, p, d;
      for (const l of t) {
        if (!c.isArray(l))
          throw TypeError("Object iterator must return a key-value pair");
        u[d = l[0]] = (p = u[d]) ? c.isArray(p) ? [...p, l[1]] : [p, l[1]] : l[1];
      }
      a(u, r);
    } else
      t != null && i(r, t, n);
    return this;
  }
  get(t, r) {
    if (t = ce(t), t) {
      const n = c.findKey(this, t);
      if (n) {
        const s = this[n];
        if (!r)
          return s;
        if (r === !0)
          return Wn(s);
        if (c.isFunction(r))
          return r.call(this, s, n);
        if (c.isRegExp(r))
          return r.exec(s);
        throw new TypeError("parser must be boolean|regexp|function");
      }
    }
  }
  has(t, r) {
    if (t = ce(t), t) {
      const n = c.findKey(this, t);
      return !!(n && this[n] !== void 0 && (!r || Ue(this, this[n], n, r)));
    }
    return !1;
  }
  delete(t, r) {
    const n = this;
    let s = !1;
    function i(a) {
      if (a = ce(a), a) {
        const u = c.findKey(n, a);
        u && (!r || Ue(n, n[u], u, r)) && (delete n[u], s = !0);
      }
    }
    return c.isArray(t) ? t.forEach(i) : i(t), s;
  }
  clear(t) {
    const r = Object.keys(this);
    let n = r.length, s = !1;
    for (; n--; ) {
      const i = r[n];
      (!t || Ue(this, this[i], i, t, !0)) && (delete this[i], s = !0);
    }
    return s;
  }
  normalize(t) {
    const r = this, n = {};
    return c.forEach(this, (s, i) => {
      const a = c.findKey(n, i);
      if (a) {
        r[a] = ge(s), delete r[i];
        return;
      }
      const u = t ? zn(i) : String(i).trim();
      u !== i && delete r[i], r[u] = ge(s), n[u] = !0;
    }), this;
  }
  concat(...t) {
    return this.constructor.concat(this, ...t);
  }
  toJSON(t) {
    const r = /* @__PURE__ */ Object.create(null);
    return c.forEach(this, (n, s) => {
      n != null && n !== !1 && (r[s] = t && c.isArray(n) ? n.join(", ") : n);
    }), r;
  }
  [Symbol.iterator]() {
    return Object.entries(this.toJSON())[Symbol.iterator]();
  }
  toString() {
    return Object.entries(this.toJSON()).map(([t, r]) => t + ": " + r).join(`
`);
  }
  getSetCookie() {
    return this.get("set-cookie") || [];
  }
  get [Symbol.toStringTag]() {
    return "AxiosHeaders";
  }
  static from(t) {
    return t instanceof this ? t : new this(t);
  }
  static concat(t, ...r) {
    const n = new this(t);
    return r.forEach((s) => n.set(s)), n;
  }
  static accessor(t) {
    const n = (this[At] = this[At] = {
      accessors: {}
    }).accessors, s = this.prototype;
    function i(a) {
      const u = ce(a);
      n[u] || (Jn(s, a), n[u] = !0);
    }
    return c.isArray(t) ? t.forEach(i) : i(t), this;
  }
};
B.accessor(["Content-Type", "Content-Length", "Accept", "Accept-Encoding", "User-Agent", "Authorization"]);
c.reduceDescriptors(B.prototype, ({ value: e }, t) => {
  let r = t[0].toUpperCase() + t.slice(1);
  return {
    get: () => e,
    set(n) {
      this[r] = n;
    }
  };
});
c.freezeMethods(B);
function Be(e, t) {
  const r = this || pe, n = t || r, s = B.from(n.headers);
  let i = n.data;
  return c.forEach(e, function(u) {
    i = u.call(r, i, s.normalize(), t ? t.status : void 0);
  }), s.normalize(), i;
}
function Zt(e) {
  return !!(e && e.__CANCEL__);
}
function re(e, t, r) {
  w.call(this, e ?? "canceled", w.ERR_CANCELED, t, r), this.name = "CanceledError";
}
c.inherits(re, w, {
  __CANCEL__: !0
});
function Qt(e, t, r) {
  const n = r.config.validateStatus;
  !r.status || !n || n(r.status) ? e(r) : t(new w(
    "Request failed with status code " + r.status,
    [w.ERR_BAD_REQUEST, w.ERR_BAD_RESPONSE][Math.floor(r.status / 100) - 4],
    r.config,
    r.request,
    r
  ));
}
function Kn(e) {
  const t = /^([-+\w]{1,25})(:?\/\/|:)/.exec(e);
  return t && t[1] || "";
}
function Yn(e, t) {
  e = e || 10;
  const r = new Array(e), n = new Array(e);
  let s = 0, i = 0, a;
  return t = t !== void 0 ? t : 1e3, function(p) {
    const d = Date.now(), l = n[i];
    a || (a = d), r[s] = p, n[s] = d;
    let m = i, S = 0;
    for (; m !== s; )
      S += r[m++], m = m % e;
    if (s = (s + 1) % e, s === i && (i = (i + 1) % e), d - a < t)
      return;
    const x = l && d - l;
    return x ? Math.round(S * 1e3 / x) : void 0;
  };
}
function Xn(e, t) {
  let r = 0, n = 1e3 / t, s, i;
  const a = (d, l = Date.now()) => {
    r = l, s = null, i && (clearTimeout(i), i = null), e(...d);
  };
  return [(...d) => {
    const l = Date.now(), m = l - r;
    m >= n ? a(d, l) : (s = d, i || (i = setTimeout(() => {
      i = null, a(s);
    }, n - m)));
  }, () => s && a(s)];
}
const Re = (e, t, r = 3) => {
  let n = 0;
  const s = Yn(50, 250);
  return Xn((i) => {
    const a = i.loaded, u = i.lengthComputable ? i.total : void 0, p = a - n, d = s(p), l = a <= u;
    n = a;
    const m = {
      loaded: a,
      total: u,
      progress: u ? a / u : void 0,
      bytes: p,
      rate: d || void 0,
      estimated: d && u && l ? (u - a) / d : void 0,
      event: i,
      lengthComputable: u != null,
      [t ? "download" : "upload"]: !0
    };
    e(m);
  }, r);
}, xt = (e, t) => {
  const r = e != null;
  return [(n) => t[0]({
    lengthComputable: r,
    total: e,
    loaded: n
  }), t[1]];
}, Ct = (e) => (...t) => c.asap(() => e(...t)), Gn = N.hasStandardBrowserEnv ? /* @__PURE__ */ ((e, t) => (r) => (r = new URL(r, N.origin), e.protocol === r.protocol && e.host === r.host && (t || e.port === r.port)))(
  new URL(N.origin),
  N.navigator && /(msie|trident)/i.test(N.navigator.userAgent)
) : () => !0, Zn = N.hasStandardBrowserEnv ? (
  // Standard browser envs support document.cookie
  {
    write(e, t, r, n, s, i) {
      const a = [e + "=" + encodeURIComponent(t)];
      c.isNumber(r) && a.push("expires=" + new Date(r).toGMTString()), c.isString(n) && a.push("path=" + n), c.isString(s) && a.push("domain=" + s), i === !0 && a.push("secure"), document.cookie = a.join("; ");
    },
    read(e) {
      const t = document.cookie.match(new RegExp("(^|;\\s*)(" + e + ")=([^;]*)"));
      return t ? decodeURIComponent(t[3]) : null;
    },
    remove(e) {
      this.write(e, "", Date.now() - 864e5);
    }
  }
) : (
  // Non-standard browser env (web workers, react-native) lack needed support.
  {
    write() {
    },
    read() {
      return null;
    },
    remove() {
    }
  }
);
function Qn(e) {
  return /^([a-z][a-z\d+\-.]*:)?\/\//i.test(e);
}
function es(e, t) {
  return t ? e.replace(/\/?\/$/, "") + "/" + t.replace(/^\/+/, "") : e;
}
function er(e, t, r) {
  let n = !Qn(t);
  return e && (n || r == !1) ? es(e, t) : t;
}
const Pt = (e) => e instanceof B ? { ...e } : e;
function G(e, t) {
  t = t || {};
  const r = {};
  function n(d, l, m, S) {
    return c.isPlainObject(d) && c.isPlainObject(l) ? c.merge.call({ caseless: S }, d, l) : c.isPlainObject(l) ? c.merge({}, l) : c.isArray(l) ? l.slice() : l;
  }
  function s(d, l, m, S) {
    if (c.isUndefined(l)) {
      if (!c.isUndefined(d))
        return n(void 0, d, m, S);
    } else return n(d, l, m, S);
  }
  function i(d, l) {
    if (!c.isUndefined(l))
      return n(void 0, l);
  }
  function a(d, l) {
    if (c.isUndefined(l)) {
      if (!c.isUndefined(d))
        return n(void 0, d);
    } else return n(void 0, l);
  }
  function u(d, l, m) {
    if (m in t)
      return n(d, l);
    if (m in e)
      return n(void 0, d);
  }
  const p = {
    url: i,
    method: i,
    data: i,
    baseURL: a,
    transformRequest: a,
    transformResponse: a,
    paramsSerializer: a,
    timeout: a,
    timeoutMessage: a,
    withCredentials: a,
    withXSRFToken: a,
    adapter: a,
    responseType: a,
    xsrfCookieName: a,
    xsrfHeaderName: a,
    onUploadProgress: a,
    onDownloadProgress: a,
    decompress: a,
    maxContentLength: a,
    maxBodyLength: a,
    beforeRedirect: a,
    transport: a,
    httpAgent: a,
    httpsAgent: a,
    cancelToken: a,
    socketPath: a,
    responseEncoding: a,
    validateStatus: u,
    headers: (d, l, m) => s(Pt(d), Pt(l), m, !0)
  };
  return c.forEach(Object.keys({ ...e, ...t }), function(l) {
    const m = p[l] || s, S = m(e[l], t[l], l);
    c.isUndefined(S) && m !== u || (r[l] = S);
  }), r;
}
const tr = (e) => {
  const t = G({}, e);
  let { data: r, withXSRFToken: n, xsrfHeaderName: s, xsrfCookieName: i, headers: a, auth: u } = t;
  t.headers = a = B.from(a), t.url = Yt(er(t.baseURL, t.url, t.allowAbsoluteUrls), e.params, e.paramsSerializer), u && a.set(
    "Authorization",
    "Basic " + btoa((u.username || "") + ":" + (u.password ? unescape(encodeURIComponent(u.password)) : ""))
  );
  let p;
  if (c.isFormData(r)) {
    if (N.hasStandardBrowserEnv || N.hasStandardBrowserWebWorkerEnv)
      a.setContentType(void 0);
    else if ((p = a.getContentType()) !== !1) {
      const [d, ...l] = p ? p.split(";").map((m) => m.trim()).filter(Boolean) : [];
      a.setContentType([d || "multipart/form-data", ...l].join("; "));
    }
  }
  if (N.hasStandardBrowserEnv && (n && c.isFunction(n) && (n = n(t)), n || n !== !1 && Gn(t.url))) {
    const d = s && i && Zn.read(i);
    d && a.set(s, d);
  }
  return t;
}, ts = typeof XMLHttpRequest < "u", rs = ts && function(e) {
  return new Promise(function(r, n) {
    const s = tr(e);
    let i = s.data;
    const a = B.from(s.headers).normalize();
    let { responseType: u, onUploadProgress: p, onDownloadProgress: d } = s, l, m, S, x, y;
    function g() {
      x && x(), y && y(), s.cancelToken && s.cancelToken.unsubscribe(l), s.signal && s.signal.removeEventListener("abort", l);
    }
    let b = new XMLHttpRequest();
    b.open(s.method.toUpperCase(), s.url, !0), b.timeout = s.timeout;
    function _() {
      if (!b)
        return;
      const F = B.from(
        "getAllResponseHeaders" in b && b.getAllResponseHeaders()
      ), k = {
        data: !u || u === "text" || u === "json" ? b.responseText : b.response,
        status: b.status,
        statusText: b.statusText,
        headers: F,
        config: e,
        request: b
      };
      Qt(function(W) {
        r(W), g();
      }, function(W) {
        n(W), g();
      }, k), b = null;
    }
    "onloadend" in b ? b.onloadend = _ : b.onreadystatechange = function() {
      !b || b.readyState !== 4 || b.status === 0 && !(b.responseURL && b.responseURL.indexOf("file:") === 0) || setTimeout(_);
    }, b.onabort = function() {
      b && (n(new w("Request aborted", w.ECONNABORTED, e, b)), b = null);
    }, b.onerror = function() {
      n(new w("Network Error", w.ERR_NETWORK, e, b)), b = null;
    }, b.ontimeout = function() {
      let q = s.timeout ? "timeout of " + s.timeout + "ms exceeded" : "timeout exceeded";
      const k = s.transitional || Xt;
      s.timeoutErrorMessage && (q = s.timeoutErrorMessage), n(new w(
        q,
        k.clarifyTimeoutError ? w.ETIMEDOUT : w.ECONNABORTED,
        e,
        b
      )), b = null;
    }, i === void 0 && a.setContentType(null), "setRequestHeader" in b && c.forEach(a.toJSON(), function(q, k) {
      b.setRequestHeader(k, q);
    }), c.isUndefined(s.withCredentials) || (b.withCredentials = !!s.withCredentials), u && u !== "json" && (b.responseType = s.responseType), d && ([S, y] = Re(d, !0), b.addEventListener("progress", S)), p && b.upload && ([m, x] = Re(p), b.upload.addEventListener("progress", m), b.upload.addEventListener("loadend", x)), (s.cancelToken || s.signal) && (l = (F) => {
      b && (n(!F || F.type ? new re(null, e, b) : F), b.abort(), b = null);
    }, s.cancelToken && s.cancelToken.subscribe(l), s.signal && (s.signal.aborted ? l() : s.signal.addEventListener("abort", l)));
    const O = Kn(s.url);
    if (O && N.protocols.indexOf(O) === -1) {
      n(new w("Unsupported protocol " + O + ":", w.ERR_BAD_REQUEST, e));
      return;
    }
    b.send(i || null);
  });
}, ns = (e, t) => {
  const { length: r } = e = e ? e.filter(Boolean) : [];
  if (t || r) {
    let n = new AbortController(), s;
    const i = function(d) {
      if (!s) {
        s = !0, u();
        const l = d instanceof Error ? d : this.reason;
        n.abort(l instanceof w ? l : new re(l instanceof Error ? l.message : l));
      }
    };
    let a = t && setTimeout(() => {
      a = null, i(new w(`timeout ${t} of ms exceeded`, w.ETIMEDOUT));
    }, t);
    const u = () => {
      e && (a && clearTimeout(a), a = null, e.forEach((d) => {
        d.unsubscribe ? d.unsubscribe(i) : d.removeEventListener("abort", i);
      }), e = null);
    };
    e.forEach((d) => d.addEventListener("abort", i));
    const { signal: p } = n;
    return p.unsubscribe = () => c.asap(u), p;
  }
}, ss = function* (e, t) {
  let r = e.byteLength;
  if (r < t) {
    yield e;
    return;
  }
  let n = 0, s;
  for (; n < r; )
    s = n + t, yield e.slice(n, s), n = s;
}, os = async function* (e, t) {
  for await (const r of is(e))
    yield* ss(r, t);
}, is = async function* (e) {
  if (e[Symbol.asyncIterator]) {
    yield* e;
    return;
  }
  const t = e.getReader();
  try {
    for (; ; ) {
      const { done: r, value: n } = await t.read();
      if (r)
        break;
      yield n;
    }
  } finally {
    await t.cancel();
  }
}, Ft = (e, t, r, n) => {
  const s = os(e, t);
  let i = 0, a, u = (p) => {
    a || (a = !0, n && n(p));
  };
  return new ReadableStream({
    async pull(p) {
      try {
        const { done: d, value: l } = await s.next();
        if (d) {
          u(), p.close();
          return;
        }
        let m = l.byteLength;
        if (r) {
          let S = i += m;
          r(S);
        }
        p.enqueue(new Uint8Array(l));
      } catch (d) {
        throw u(d), d;
      }
    },
    cancel(p) {
      return u(p), s.return();
    }
  }, {
    highWaterMark: 2
  });
}, Ae = typeof fetch == "function" && typeof Request == "function" && typeof Response == "function", rr = Ae && typeof ReadableStream == "function", as = Ae && (typeof TextEncoder == "function" ? /* @__PURE__ */ ((e) => (t) => e.encode(t))(new TextEncoder()) : async (e) => new Uint8Array(await new Response(e).arrayBuffer())), nr = (e, ...t) => {
  try {
    return !!e(...t);
  } catch {
    return !1;
  }
}, cs = rr && nr(() => {
  let e = !1;
  const t = new Request(N.origin, {
    body: new ReadableStream(),
    method: "POST",
    get duplex() {
      return e = !0, "half";
    }
  }).headers.has("Content-Type");
  return e && !t;
}), jt = 64 * 1024, We = rr && nr(() => c.isReadableStream(new Response("").body)), Se = {
  stream: We && ((e) => e.body)
};
Ae && ((e) => {
  ["text", "arrayBuffer", "blob", "formData", "stream"].forEach((t) => {
    !Se[t] && (Se[t] = c.isFunction(e[t]) ? (r) => r[t]() : (r, n) => {
      throw new w(`Response type '${t}' is not supported`, w.ERR_NOT_SUPPORT, n);
    });
  });
})(new Response());
const us = async (e) => {
  if (e == null)
    return 0;
  if (c.isBlob(e))
    return e.size;
  if (c.isSpecCompliantForm(e))
    return (await new Request(N.origin, {
      method: "POST",
      body: e
    }).arrayBuffer()).byteLength;
  if (c.isArrayBufferView(e) || c.isArrayBuffer(e))
    return e.byteLength;
  if (c.isURLSearchParams(e) && (e = e + ""), c.isString(e))
    return (await as(e)).byteLength;
}, ls = async (e, t) => {
  const r = c.toFiniteNumber(e.getContentLength());
  return r ?? us(t);
}, fs = Ae && (async (e) => {
  let {
    url: t,
    method: r,
    data: n,
    signal: s,
    cancelToken: i,
    timeout: a,
    onDownloadProgress: u,
    onUploadProgress: p,
    responseType: d,
    headers: l,
    withCredentials: m = "same-origin",
    fetchOptions: S
  } = tr(e);
  d = d ? (d + "").toLowerCase() : "text";
  let x = ns([s, i && i.toAbortSignal()], a), y;
  const g = x && x.unsubscribe && (() => {
    x.unsubscribe();
  });
  let b;
  try {
    if (p && cs && r !== "get" && r !== "head" && (b = await ls(l, n)) !== 0) {
      let k = new Request(t, {
        method: "POST",
        body: n,
        duplex: "half"
      }), $;
      if (c.isFormData(n) && ($ = k.headers.get("content-type")) && l.setContentType($), k.body) {
        const [W, Z] = xt(
          b,
          Re(Ct(p))
        );
        n = Ft(k.body, jt, W, Z);
      }
    }
    c.isString(m) || (m = m ? "include" : "omit");
    const _ = "credentials" in Request.prototype;
    y = new Request(t, {
      ...S,
      signal: x,
      method: r.toUpperCase(),
      headers: l.normalize().toJSON(),
      body: n,
      duplex: "half",
      credentials: _ ? m : void 0
    });
    let O = await fetch(y, S);
    const F = We && (d === "stream" || d === "response");
    if (We && (u || F && g)) {
      const k = {};
      ["status", "statusText", "headers"].forEach((ne) => {
        k[ne] = O[ne];
      });
      const $ = c.toFiniteNumber(O.headers.get("content-length")), [W, Z] = u && xt(
        $,
        Re(Ct(u), !0)
      ) || [];
      O = new Response(
        Ft(O.body, jt, W, () => {
          Z && Z(), g && g();
        }),
        k
      );
    }
    d = d || "text";
    let q = await Se[c.findKey(Se, d) || "text"](O, e);
    return !F && g && g(), await new Promise((k, $) => {
      Qt(k, $, {
        data: q,
        headers: B.from(O.headers),
        status: O.status,
        statusText: O.statusText,
        config: e,
        request: y
      });
    });
  } catch (_) {
    throw g && g(), _ && _.name === "TypeError" && /Load failed|fetch/i.test(_.message) ? Object.assign(
      new w("Network Error", w.ERR_NETWORK, e, y),
      {
        cause: _.cause || _
      }
    ) : w.from(_, _ && _.code, e, y);
  }
}), Ve = {
  http: _n,
  xhr: rs,
  fetch: fs
};
c.forEach(Ve, (e, t) => {
  if (e) {
    try {
      Object.defineProperty(e, "name", { value: t });
    } catch {
    }
    Object.defineProperty(e, "adapterName", { value: t });
  }
});
const kt = (e) => `- ${e}`, ds = (e) => c.isFunction(e) || e === null || e === !1, sr = {
  getAdapter: (e) => {
    e = c.isArray(e) ? e : [e];
    const { length: t } = e;
    let r, n;
    const s = {};
    for (let i = 0; i < t; i++) {
      r = e[i];
      let a;
      if (n = r, !ds(r) && (n = Ve[(a = String(r)).toLowerCase()], n === void 0))
        throw new w(`Unknown adapter '${a}'`);
      if (n)
        break;
      s[a || "#" + i] = n;
    }
    if (!n) {
      const i = Object.entries(s).map(
        ([u, p]) => `adapter ${u} ` + (p === !1 ? "is not supported by the environment" : "is not available in the build")
      );
      let a = t ? i.length > 1 ? `since :
` + i.map(kt).join(`
`) : " " + kt(i[0]) : "as no adapter specified";
      throw new w(
        "There is no suitable adapter to dispatch the request " + a,
        "ERR_NOT_SUPPORT"
      );
    }
    return n;
  },
  adapters: Ve
};
function Ie(e) {
  if (e.cancelToken && e.cancelToken.throwIfRequested(), e.signal && e.signal.aborted)
    throw new re(null, e);
}
function Nt(e) {
  return Ie(e), e.headers = B.from(e.headers), e.data = Be.call(
    e,
    e.transformRequest
  ), ["post", "put", "patch"].indexOf(e.method) !== -1 && e.headers.setContentType("application/x-www-form-urlencoded", !1), sr.getAdapter(e.adapter || pe.adapter)(e).then(function(n) {
    return Ie(e), n.data = Be.call(
      e,
      e.transformResponse,
      n
    ), n.headers = B.from(n.headers), n;
  }, function(n) {
    return Zt(n) || (Ie(e), n && n.response && (n.response.data = Be.call(
      e,
      e.transformResponse,
      n.response
    ), n.response.headers = B.from(n.response.headers))), Promise.reject(n);
  });
}
const or = "1.11.0", xe = {};
["object", "boolean", "number", "function", "string", "symbol"].forEach((e, t) => {
  xe[e] = function(n) {
    return typeof n === e || "a" + (t < 1 ? "n " : " ") + e;
  };
});
const Dt = {};
xe.transitional = function(t, r, n) {
  function s(i, a) {
    return "[Axios v" + or + "] Transitional option '" + i + "'" + a + (n ? ". " + n : "");
  }
  return (i, a, u) => {
    if (t === !1)
      throw new w(
        s(a, " has been removed" + (r ? " in " + r : "")),
        w.ERR_DEPRECATED
      );
    return r && !Dt[a] && (Dt[a] = !0, console.warn(
      s(
        a,
        " has been deprecated since v" + r + " and will be removed in the near future"
      )
    )), t ? t(i, a, u) : !0;
  };
};
xe.spelling = function(t) {
  return (r, n) => (console.warn(`${n} is likely a misspelling of ${t}`), !0);
};
function ps(e, t, r) {
  if (typeof e != "object")
    throw new w("options must be an object", w.ERR_BAD_OPTION_VALUE);
  const n = Object.keys(e);
  let s = n.length;
  for (; s-- > 0; ) {
    const i = n[s], a = t[i];
    if (a) {
      const u = e[i], p = u === void 0 || a(u, i, e);
      if (p !== !0)
        throw new w("option " + i + " must be " + p, w.ERR_BAD_OPTION_VALUE);
      continue;
    }
    if (r !== !0)
      throw new w("Unknown option " + i, w.ERR_BAD_OPTION);
  }
}
const we = {
  assertOptions: ps,
  validators: xe
}, H = we.validators;
let X = class {
  constructor(t) {
    this.defaults = t || {}, this.interceptors = {
      request: new _t(),
      response: new _t()
    };
  }
  /**
   * Dispatch a request
   *
   * @param {String|Object} configOrUrl The config specific for this request (merged with this.defaults)
   * @param {?Object} config
   *
   * @returns {Promise} The Promise to be fulfilled
   */
  async request(t, r) {
    try {
      return await this._request(t, r);
    } catch (n) {
      if (n instanceof Error) {
        let s = {};
        Error.captureStackTrace ? Error.captureStackTrace(s) : s = new Error();
        const i = s.stack ? s.stack.replace(/^.+\n/, "") : "";
        try {
          n.stack ? i && !String(n.stack).endsWith(i.replace(/^.+\n.+\n/, "")) && (n.stack += `
` + i) : n.stack = i;
        } catch {
        }
      }
      throw n;
    }
  }
  _request(t, r) {
    typeof t == "string" ? (r = r || {}, r.url = t) : r = t || {}, r = G(this.defaults, r);
    const { transitional: n, paramsSerializer: s, headers: i } = r;
    n !== void 0 && we.assertOptions(n, {
      silentJSONParsing: H.transitional(H.boolean),
      forcedJSONParsing: H.transitional(H.boolean),
      clarifyTimeoutError: H.transitional(H.boolean)
    }, !1), s != null && (c.isFunction(s) ? r.paramsSerializer = {
      serialize: s
    } : we.assertOptions(s, {
      encode: H.function,
      serialize: H.function
    }, !0)), r.allowAbsoluteUrls !== void 0 || (this.defaults.allowAbsoluteUrls !== void 0 ? r.allowAbsoluteUrls = this.defaults.allowAbsoluteUrls : r.allowAbsoluteUrls = !0), we.assertOptions(r, {
      baseUrl: H.spelling("baseURL"),
      withXsrfToken: H.spelling("withXSRFToken")
    }, !0), r.method = (r.method || this.defaults.method || "get").toLowerCase();
    let a = i && c.merge(
      i.common,
      i[r.method]
    );
    i && c.forEach(
      ["delete", "get", "head", "post", "put", "patch", "common"],
      (y) => {
        delete i[y];
      }
    ), r.headers = B.concat(a, i);
    const u = [];
    let p = !0;
    this.interceptors.request.forEach(function(g) {
      typeof g.runWhen == "function" && g.runWhen(r) === !1 || (p = p && g.synchronous, u.unshift(g.fulfilled, g.rejected));
    });
    const d = [];
    this.interceptors.response.forEach(function(g) {
      d.push(g.fulfilled, g.rejected);
    });
    let l, m = 0, S;
    if (!p) {
      const y = [Nt.bind(this), void 0];
      for (y.unshift(...u), y.push(...d), S = y.length, l = Promise.resolve(r); m < S; )
        l = l.then(y[m++], y[m++]);
      return l;
    }
    S = u.length;
    let x = r;
    for (m = 0; m < S; ) {
      const y = u[m++], g = u[m++];
      try {
        x = y(x);
      } catch (b) {
        g.call(this, b);
        break;
      }
    }
    try {
      l = Nt.call(this, x);
    } catch (y) {
      return Promise.reject(y);
    }
    for (m = 0, S = d.length; m < S; )
      l = l.then(d[m++], d[m++]);
    return l;
  }
  getUri(t) {
    t = G(this.defaults, t);
    const r = er(t.baseURL, t.url, t.allowAbsoluteUrls);
    return Yt(r, t.params, t.paramsSerializer);
  }
};
c.forEach(["delete", "get", "head", "options"], function(t) {
  X.prototype[t] = function(r, n) {
    return this.request(G(n || {}, {
      method: t,
      url: r,
      data: (n || {}).data
    }));
  };
});
c.forEach(["post", "put", "patch"], function(t) {
  function r(n) {
    return function(i, a, u) {
      return this.request(G(u || {}, {
        method: t,
        headers: n ? {
          "Content-Type": "multipart/form-data"
        } : {},
        url: i,
        data: a
      }));
    };
  }
  X.prototype[t] = r(), X.prototype[t + "Form"] = r(!0);
});
let hs = class ir {
  constructor(t) {
    if (typeof t != "function")
      throw new TypeError("executor must be a function.");
    let r;
    this.promise = new Promise(function(i) {
      r = i;
    });
    const n = this;
    this.promise.then((s) => {
      if (!n._listeners) return;
      let i = n._listeners.length;
      for (; i-- > 0; )
        n._listeners[i](s);
      n._listeners = null;
    }), this.promise.then = (s) => {
      let i;
      const a = new Promise((u) => {
        n.subscribe(u), i = u;
      }).then(s);
      return a.cancel = function() {
        n.unsubscribe(i);
      }, a;
    }, t(function(i, a, u) {
      n.reason || (n.reason = new re(i, a, u), r(n.reason));
    });
  }
  /**
   * Throws a `CanceledError` if cancellation has been requested.
   */
  throwIfRequested() {
    if (this.reason)
      throw this.reason;
  }
  /**
   * Subscribe to the cancel signal
   */
  subscribe(t) {
    if (this.reason) {
      t(this.reason);
      return;
    }
    this._listeners ? this._listeners.push(t) : this._listeners = [t];
  }
  /**
   * Unsubscribe from the cancel signal
   */
  unsubscribe(t) {
    if (!this._listeners)
      return;
    const r = this._listeners.indexOf(t);
    r !== -1 && this._listeners.splice(r, 1);
  }
  toAbortSignal() {
    const t = new AbortController(), r = (n) => {
      t.abort(n);
    };
    return this.subscribe(r), t.signal.unsubscribe = () => this.unsubscribe(r), t.signal;
  }
  /**
   * Returns an object that contains a new `CancelToken` and a function that, when called,
   * cancels the `CancelToken`.
   */
  static source() {
    let t;
    return {
      token: new ir(function(s) {
        t = s;
      }),
      cancel: t
    };
  }
};
function ms(e) {
  return function(r) {
    return e.apply(null, r);
  };
}
function ys(e) {
  return c.isObject(e) && e.isAxiosError === !0;
}
const ze = {
  Continue: 100,
  SwitchingProtocols: 101,
  Processing: 102,
  EarlyHints: 103,
  Ok: 200,
  Created: 201,
  Accepted: 202,
  NonAuthoritativeInformation: 203,
  NoContent: 204,
  ResetContent: 205,
  PartialContent: 206,
  MultiStatus: 207,
  AlreadyReported: 208,
  ImUsed: 226,
  MultipleChoices: 300,
  MovedPermanently: 301,
  Found: 302,
  SeeOther: 303,
  NotModified: 304,
  UseProxy: 305,
  Unused: 306,
  TemporaryRedirect: 307,
  PermanentRedirect: 308,
  BadRequest: 400,
  Unauthorized: 401,
  PaymentRequired: 402,
  Forbidden: 403,
  NotFound: 404,
  MethodNotAllowed: 405,
  NotAcceptable: 406,
  ProxyAuthenticationRequired: 407,
  RequestTimeout: 408,
  Conflict: 409,
  Gone: 410,
  LengthRequired: 411,
  PreconditionFailed: 412,
  PayloadTooLarge: 413,
  UriTooLong: 414,
  UnsupportedMediaType: 415,
  RangeNotSatisfiable: 416,
  ExpectationFailed: 417,
  ImATeapot: 418,
  MisdirectedRequest: 421,
  UnprocessableEntity: 422,
  Locked: 423,
  FailedDependency: 424,
  TooEarly: 425,
  UpgradeRequired: 426,
  PreconditionRequired: 428,
  TooManyRequests: 429,
  RequestHeaderFieldsTooLarge: 431,
  UnavailableForLegalReasons: 451,
  InternalServerError: 500,
  NotImplemented: 501,
  BadGateway: 502,
  ServiceUnavailable: 503,
  GatewayTimeout: 504,
  HttpVersionNotSupported: 505,
  VariantAlsoNegotiates: 506,
  InsufficientStorage: 507,
  LoopDetected: 508,
  NotExtended: 510,
  NetworkAuthenticationRequired: 511
};
Object.entries(ze).forEach(([e, t]) => {
  ze[t] = e;
});
function ar(e) {
  const t = new X(e), r = Ut(X.prototype.request, t);
  return c.extend(r, X.prototype, t, { allOwnKeys: !0 }), c.extend(r, t, null, { allOwnKeys: !0 }), r.create = function(s) {
    return ar(G(e, s));
  }, r;
}
const P = ar(pe);
P.Axios = X;
P.CanceledError = re;
P.CancelToken = hs;
P.isCancel = Zt;
P.VERSION = or;
P.toFormData = _e;
P.AxiosError = w;
P.Cancel = P.CanceledError;
P.all = function(t) {
  return Promise.all(t);
};
P.spread = ms;
P.isAxiosError = ys;
P.mergeConfig = G;
P.AxiosHeaders = B;
P.formToJSON = (e) => Gt(c.isHTMLForm(e) ? new FormData(e) : e);
P.getAdapter = sr.getAdapter;
P.HttpStatusCode = ze;
P.default = P;
const {
  Axios: ws,
  AxiosError: Rs,
  CanceledError: Ss,
  isCancel: Os,
  CancelToken: Ts,
  VERSION: vs,
  all: _s,
  Cancel: As,
  isAxiosError: xs,
  spread: Cs,
  toFormData: Ps,
  AxiosHeaders: Fs,
  HttpStatusCode: js,
  formToJSON: ks,
  getAdapter: Ns,
  mergeConfig: Ds
} = P, Ls = ({ topic: e }) => {
  const [t, r] = wt([]), [n, s] = wt(!0);
  return Ur(() => {
    (async () => {
      try {
        const a = await P.post(
          "http://34.30.201.70:5001/getHeadlines",
          { topic: e },
          { headers: { "Content-Type": "application/json" } }
        );
        r(a.data);
      } catch (a) {
        console.error("Failed to fetch headlines:", a), r([]);
      } finally {
        s(!1);
      }
    })();
  }, [e]), n ? /* @__PURE__ */ V.jsx("p", { children: "Loading news..." }) : /* @__PURE__ */ V.jsxs("div", { style: { color: "white", fontFamily: "Arial", padding: "1rem", backgroundColor: "#1e293b" }, children: [
    /* @__PURE__ */ V.jsxs("h3", { children: [
      "📰 Top News for ",
      /* @__PURE__ */ V.jsx("em", { children: e })
    ] }),
    t.length === 0 && /* @__PURE__ */ V.jsx("p", { children: "No news found for this topic." }),
    t.map((i, a) => /* @__PURE__ */ V.jsxs("div", { style: { margin: "1rem 0", borderBottom: "1px solid #334155", paddingBottom: "0.5rem" }, children: [
      /* @__PURE__ */ V.jsx("a", { href: i.url, target: "_blank", rel: "noopener noreferrer", style: { color: "#38bdf8", fontWeight: "bold" }, children: i.title }),
      /* @__PURE__ */ V.jsxs("p", { style: { fontSize: "0.9rem", color: "#94a3b8" }, children: [
        i.source,
        " — ",
        new Date(i.publishedAt).toLocaleString()
      ] }),
      /* @__PURE__ */ V.jsx("p", { children: i.description })
    ] }, a))
  ] });
};
export {
  Ls as NewsPluginComponent
};
