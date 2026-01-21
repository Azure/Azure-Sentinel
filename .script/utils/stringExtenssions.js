"use strict";
String.prototype.endsWithAny = function (suffixes) {
    return suffixes.some(suffix => this.endsWith(suffix));
};
String.prototype.startsWithAny = function (prefixes) {
    return prefixes.some(prefix => this.startsWith(prefix));
};
//# sourceMappingURL=stringExtenssions.js.map