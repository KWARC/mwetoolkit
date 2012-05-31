/^typedef struct .*\{/,/^\}/p
/^struct .*\{/,/^\};/p
/^union .*\{/,/\};/p
/^typedef .*;/p
/^#define .*\\$/,/[^\]$/p
/^#define .*\\$/!{
/^[[:space:]]*#[[:alnum:]]/p
}
/^typedef|^struct|^union/!{
s/^([A-Za-z][^\{]*)=.*/extern \1;/p
s/^([A-Za-z][^\{]*[^ \{])[[:space:]]*\{$/\1;/gp
/^([A-Za-z][^\{]*[^ \{])[[:space:]]*,$/,/.*\{$/ {
s/[[:space:]]*\{$/;/g;
p
}
}
