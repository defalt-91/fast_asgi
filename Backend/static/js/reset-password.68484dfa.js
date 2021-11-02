(window.webpackJsonp=window.webpackJsonp||[]).push([["reset-password"],{"0813":function(e,t,r){"use strict";r.r(t);var o=r("a34a"),n=r.n(o),a=r("9ab4"),s=r("60a3"),i=r("5f03"),c=r("635a"),u=r("d568");function _typeof(e){return(_typeof="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function _typeof(e){return typeof e}:function _typeof(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function asyncGeneratorStep(e,t,r,o,n,a,s){try{var i=e[a](s),c=i.value}catch(e){return void r(e)}i.done?t(c):Promise.resolve(c).then(o,n)}function _classCallCheck(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function _defineProperties(e,t){for(var r=0;r<t.length;r++){var o=t[r];o.enumerable=o.enumerable||!1,o.configurable=!0,"value"in o&&(o.writable=!0),Object.defineProperty(e,o.key,o)}}function _setPrototypeOf(e,t){return(_setPrototypeOf=Object.setPrototypeOf||function _setPrototypeOf(e,t){return e.__proto__=t,e})(e,t)}function _createSuper(e){var t=function _isNativeReflectConstruct(){if("undefined"==typeof Reflect||!Reflect.construct)return!1;if(Reflect.construct.sham)return!1;if("function"==typeof Proxy)return!0;try{return Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){}))),!0}catch(e){return!1}}();return function _createSuperInternal(){var r,o=_getPrototypeOf(e);if(t){var n=_getPrototypeOf(this).constructor;r=Reflect.construct(o,arguments,n)}else r=o.apply(this,arguments);return _possibleConstructorReturn(this,r)}}function _possibleConstructorReturn(e,t){if(t&&("object"===_typeof(t)||"function"==typeof t))return t;if(void 0!==t)throw new TypeError("Derived constructors may only return object or undefined");return function _assertThisInitialized(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}(e)}function _getPrototypeOf(e){return(_getPrototypeOf=Object.setPrototypeOf?Object.getPrototypeOf:function _getPrototypeOf(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}var l=function(e){!function _inherits(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&_setPrototypeOf(e,t)}(UserProfileEdit,e);var t,r=_createSuper(UserProfileEdit);function UserProfileEdit(){var e;return _classCallCheck(this,UserProfileEdit),(e=r.apply(this,arguments)).appName=i.b,e.valid=!0,e.password1="",e.password2="",e}return function _createClass(e,t,r){return t&&_defineProperties(e.prototype,t),r&&_defineProperties(e,r),e}(UserProfileEdit,[{key:"mounted",value:function mounted(){this.checkToken()}},{key:"reset",value:function reset(){this.password1="",this.password2="",this.$validator.reset()}},{key:"cancel",value:function cancel(){this.$router.push("/")}},{key:"checkToken",value:function checkToken(){var e=this.$router.currentRoute.query.token;if(e)return e;Object(c.a)(this.$store,{content:"No token provided in the URL, start a new password recovery",color:"error"}),this.$router.push("/recover-password")}},{key:"submit",value:(t=function _asyncToGenerator(e){return function(){var t=this,r=arguments;return new Promise((function(o,n){var a=e.apply(t,r);function _next(e){asyncGeneratorStep(a,o,n,_next,_throw,"next",e)}function _throw(e){asyncGeneratorStep(a,o,n,_next,_throw,"throw",e)}_next(void 0)}))}}(n.a.mark((function _callee(){var e;return n.a.wrap((function _callee$(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,this.$validator.validateAll();case 2:if(!t.sent){t.next=8;break}if(!(e=this.checkToken())){t.next=8;break}return t.next=7,Object(u.g)(this.$store,{token:e,password:this.password1});case 7:this.$router.push("/");case 8:case"end":return t.stop()}}),_callee,this)}))),function submit(){return t.apply(this,arguments)})}]),UserProfileEdit}(s.b),f=l=Object(a.a)([s.a],l),p=r("2877"),d=Object(p.a)(f,(function(){var e=this,t=e.$createElement,r=e._self._c||t;return r("v-content",[r("v-container",{attrs:{fluid:"","fill-height":""}},[r("v-layout",{attrs:{"align-center":"","justify-center":""}},[r("v-flex",{attrs:{xs12:"",sm8:"",md4:""}},[r("v-card",{staticClass:"elevation-12"},[r("v-toolbar",{attrs:{dark:"",color:"primary"}},[r("v-toolbar-title",[e._v(e._s(e.appName)+" - Reset Password")])],1),r("v-card-text",[r("p",{staticClass:"subheading"},[e._v("Enter your new password below")]),r("v-form",{ref:"form",attrs:{"lazy-validation":""},on:{keyup:function(t){return!t.type.indexOf("key")&&e._k(t.keyCode,"enter",13,t.key,"Enter")?null:e.submit.apply(null,arguments)},submit:function(e){e.preventDefault()}},model:{value:e.valid,callback:function(t){e.valid=t},expression:"valid"}},[r("v-text-field",{directives:[{name:"validate",rawName:"v-validate",value:"required",expression:"'required'"}],ref:"password",attrs:{type:"password",label:"Password","data-vv-name":"password","data-vv-delay":"100","data-vv-rules":"required","error-messages":e.errors.first("password")},model:{value:e.password1,callback:function(t){e.password1=t},expression:"password1"}}),r("v-text-field",{directives:[{name:"validate",rawName:"v-validate",value:"required|confirmed:password",expression:"'required|confirmed:password'"}],attrs:{type:"password",label:"Confirm Password","data-vv-name":"password_confirmation","data-vv-delay":"100","data-vv-rules":"required|confirmed:$password","data-vv-as":"password","error-messages":e.errors.first("password_confirmation")},model:{value:e.password2,callback:function(t){e.password2=t},expression:"password2"}})],1)],1),r("v-card-actions",[r("v-spacer"),r("v-btn",{on:{click:e.cancel}},[e._v("Cancel")]),r("v-btn",{on:{click:e.reset}},[e._v("Clear")]),r("v-btn",{attrs:{disabled:!e.valid},on:{click:e.submit}},[e._v("Save")])],1)],1)],1)],1)],1)],1)}),[],!1,null,null,null);t.default=d.exports}}]);
//# sourceMappingURL=reset-password.68484dfa.js.map