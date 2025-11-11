interface String {
  endsWithAny: (suffixes: string[]) => boolean;
  startsWithAny: (prefixes: string[]) => boolean;
}

String.prototype.endsWithAny = function(this: string, suffixes: string[]): boolean {
  return suffixes.some(suffix => this.endsWith(suffix));
};

String.prototype.startsWithAny = function(this: string, prefixes: string[]): boolean {
  return prefixes.some(prefix => this.startsWith(prefix));
};
