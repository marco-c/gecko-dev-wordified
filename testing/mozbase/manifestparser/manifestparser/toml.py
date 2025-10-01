#
This
Source
Code
Form
is
subject
to
the
terms
of
the
Mozilla
Public
#
License
v
.
2
.
0
.
If
a
copy
of
the
MPL
was
not
distributed
with
this
file
#
You
can
obtain
one
at
http
:
/
/
mozilla
.
org
/
MPL
/
2
.
0
/
.
import
os
import
re
from
typing
import
Callable
Optional
from
tomlkit
.
items
import
Array
Table
from
tomlkit
.
toml_document
import
TOMLDocument
from
.
ini
import
combine_fields
__all__
=
[
"
read_toml
"
"
alphabetize_toml_str
"
"
add_skip_if
"
"
sort_paths
"
]
CreateBug
=
Optional
[
Callable
[
[
]
object
]
]
ListStr
=
list
[
str
]
OptionalStr
=
Optional
[
str
]
TupleStrBool
=
tuple
[
str
bool
]
FILENAME_REGEX
=
r
"
^
(
[
A
-
Za
-
z0
-
9_
.
/
-
]
*
)
(
[
Bb
]
[
Uu
]
[
Gg
]
)
(
[
-
_
]
*
)
(
[
0
-
9
]
+
)
(
[
A
-
Za
-
z0
-
9_
.
/
-
]
*
)
"
DEFAULT_SECTION
=
"
DEFAULT
"
def
sort_paths_keyfn
(
k
)
:
    
sort_paths_keyfn
.
rx
=
getattr
(
sort_paths_keyfn
"
rx
"
None
)
#
static
    
if
sort_paths_keyfn
.
rx
is
None
:
        
sort_paths_keyfn
.
rx
=
re
.
compile
(
FILENAME_REGEX
)
    
name
=
str
(
k
)
    
if
name
=
=
DEFAULT_SECTION
:
        
return
"
"
    
m
=
sort_paths_keyfn
.
rx
.
findall
(
name
)
    
if
len
(
m
)
=
=
1
and
len
(
m
[
0
]
)
=
=
5
:
        
prefix
=
m
[
0
]
[
0
]
#
text
before
"
Bug
"
        
bug
=
m
[
0
]
[
1
]
#
the
word
"
Bug
"
        
underbar
=
m
[
0
]
[
2
]
#
underbar
or
dash
(
optional
)
        
num
=
m
[
0
]
[
3
]
#
the
bug
id
        
suffix
=
m
[
0
]
[
4
]
#
text
after
the
bug
id
        
name
=
f
"
{
prefix
}
{
bug
.
lower
(
)
}
{
underbar
}
{
int
(
num
)
:
09d
}
{
suffix
}
"
        
return
name
    
return
name
def
sort_paths
(
paths
)
:
    
"
"
"
    
Returns
a
list
of
paths
(
tests
)
in
a
manifest
in
alphabetical
order
.
    
Ensures
DEFAULT
is
first
and
filenames
with
a
bug
number
are
    
in
the
proper
order
.
    
"
"
"
    
return
sorted
(
paths
key
=
sort_paths_keyfn
)
def
parse_toml_str
(
contents
)
:
    
"
"
"
    
Parse
TOML
contents
using
toml
    
"
"
"
    
try
:
        
from
tomllib
import
TOMLDecodeError
        
from
tomllib
import
loads
as
TOMLloads
    
except
ImportError
:
        
from
toml
import
TomlDecodeError
as
TOMLDecodeError
        
from
toml
import
loads
as
TOMLloads
    
error
=
None
    
manifest
=
None
    
try
:
        
manifest
=
TOMLloads
(
contents
)
    
except
TOMLDecodeError
as
pe
:
        
error
=
str
(
pe
)
    
return
error
manifest
def
parse_tomlkit_str
(
contents
)
:
    
"
"
"
    
Parse
TOML
contents
using
tomlkit
    
"
"
"
    
import
tomlkit
    
from
tomlkit
.
exceptions
import
TOMLKitError
    
error
=
None
    
manifest
=
None
    
try
:
        
manifest
=
tomlkit
.
parse
(
contents
)
    
except
TOMLKitError
as
pe
:
        
error
=
str
(
pe
)
    
return
error
manifest
def
read_toml
(
    
fp
    
defaults
=
None
    
default
=
DEFAULT_SECTION
    
_comments
=
None
    
_separators
=
None
    
strict
=
True
    
handle_defaults
=
True
    
document
=
False
    
add_line_no
=
False
)
:
    
"
"
"
    
read
a
.
toml
file
and
return
a
list
of
[
(
section
values
)
]
    
-
fp
:
file
pointer
or
path
to
read
    
-
defaults
:
default
set
of
variables
    
-
default
:
name
of
the
section
for
the
default
section
    
-
comments
:
characters
that
if
they
start
a
line
denote
a
comment
    
-
separators
:
strings
that
denote
key
value
separation
in
order
    
-
strict
:
whether
to
be
strict
about
parsing
    
-
handle_defaults
:
whether
to
incorporate
defaults
into
each
section
    
-
document
:
read
TOML
with
tomlkit
and
return
source
in
test
[
"
document
"
]
    
-
add_line_no
:
add
the
line
number
where
the
test
name
appears
in
the
file
to
the
source
.
Also
the
document
variable
must
be
set
to
True
for
this
flag
to
work
.
(
This
is
used
only
to
generate
the
documentation
)
    
"
"
"
    
#
variables
    
defaults
=
defaults
or
{
}
    
default_section
=
{
}
    
sections
=
[
]
    
if
isinstance
(
fp
str
)
:
        
filename
=
fp
        
fp
=
open
(
fp
encoding
=
"
utf
-
8
"
)
    
elif
hasattr
(
fp
"
name
"
)
:
        
filename
=
fp
.
name
    
else
:
        
filename
=
"
unknown
"
    
contents
=
fp
.
read
(
)
    
inline_comment_rx
=
re
.
compile
(
r
"
\
s
#
.
*
"
)
    
if
document
:
#
Use
tomlkit
to
parse
the
file
contents
        
error
manifest
=
parse_tomlkit_str
(
contents
)
    
else
:
        
error
manifest
=
parse_toml_str
(
contents
)
    
if
error
:
        
raise
OSError
(
f
"
Error
parsing
TOML
manifest
file
{
filename
}
:
{
error
}
"
)
    
#
handle
each
section
of
the
manifest
    
for
section
in
manifest
.
keys
(
)
:
        
current_section
=
{
}
        
for
key
in
manifest
[
section
]
.
keys
(
)
:
            
val
=
manifest
[
section
]
[
key
]
            
if
isinstance
(
val
bool
)
:
#
must
coerce
to
lowercase
string
                
if
val
:
                    
val
=
"
true
"
                
else
:
                    
val
=
"
false
"
            
elif
isinstance
(
val
list
)
:
                
new_vals
=
"
"
                
for
v
in
val
:
                    
if
len
(
new_vals
)
>
0
:
                        
new_vals
+
=
os
.
linesep
                    
new_val
=
str
(
v
)
.
strip
(
)
#
coerce
to
str
                    
comment_found
=
inline_comment_rx
.
search
(
new_val
)
                    
if
comment_found
:
                        
new_val
=
new_val
[
0
:
comment_found
.
span
(
)
[
0
]
]
                    
if
"
=
"
in
new_val
:
                        
raise
Exception
(
                            
f
"
Should
not
assign
in
{
key
}
condition
for
{
section
}
"
                        
)
                    
new_vals
+
=
new_val
                
val
=
new_vals
            
else
:
                
val
=
str
(
val
)
.
strip
(
)
#
coerce
to
str
                
comment_found
=
inline_comment_rx
.
search
(
val
)
                
if
comment_found
:
                    
val
=
val
[
0
:
comment_found
.
span
(
)
[
0
]
]
                
if
"
=
"
in
val
:
                    
raise
Exception
(
                        
f
"
Should
not
assign
in
{
key
}
condition
for
{
section
}
"
                    
)
            
current_section
[
key
]
=
val
        
if
section
.
lower
(
)
=
=
default
.
lower
(
)
:
            
default_section
=
current_section
            
#
DEFAULT
does
NOT
appear
in
the
output
        
else
:
            
sections
.
append
(
(
section
current_section
)
)
    
#
merge
global
defaults
with
the
DEFAULT
section
    
defaults
=
combine_fields
(
defaults
default_section
)
    
if
handle_defaults
:
        
#
merge
combined
defaults
into
each
section
        
sections
=
[
(
i
combine_fields
(
defaults
j
)
)
for
i
j
in
sections
]
    
if
document
and
add_line_no
:
        
#
Take
the
line
where
the
test
name
appears
in
the
file
.
        
for
i
_
in
enumerate
(
sections
)
:
            
line
=
contents
.
split
(
sections
[
i
]
[
0
]
)
[
0
]
.
count
(
os
.
linesep
)
+
1
            
manifest
.
setdefault
(
sections
[
i
]
[
0
]
{
}
)
[
"
lineno
"
]
=
str
(
line
)
    
elif
not
document
:
        
manifest
=
None
    
return
sections
defaults
manifest
def
alphabetize_toml_str
(
manifest
)
:
    
"
"
"
    
Will
take
a
TOMLkit
manifest
document
(
i
.
e
.
from
a
previous
invocation
    
of
read_toml
(
.
.
.
document
=
True
)
and
accessing
the
document
    
from
mp
.
source_documents
[
filename
]
)
and
return
it
as
a
string
    
in
sorted
order
by
section
(
i
.
e
.
test
file
name
taking
bug
ids
into
consideration
)
.
    
"
"
"
    
from
tomlkit
import
document
dumps
table
    
from
tomlkit
.
items
import
Table
    
preamble
=
"
"
    
new_manifest
=
document
(
)
    
first_section
=
False
    
sections
=
{
}
    
for
k
v
in
manifest
.
body
:
        
if
k
is
None
:
            
preamble
+
=
v
.
as_string
(
)
            
continue
        
if
not
isinstance
(
v
Table
)
:
            
raise
Exception
(
f
"
MP
TOML
illegal
keyval
in
preamble
:
{
k
}
=
{
v
}
"
)
        
section
=
None
        
if
not
first_section
:
            
if
k
=
=
DEFAULT_SECTION
:
                
new_manifest
.
add
(
k
v
)
            
else
:
                
new_manifest
.
add
(
DEFAULT_SECTION
table
(
)
)
            
first_section
=
True
        
else
:
            
values
=
v
.
items
(
)
            
if
len
(
values
)
=
=
1
:
                
for
kk
vv
in
values
:
                    
if
isinstance
(
vv
Table
)
:
#
unquoted
dotted
key
                        
section
=
f
"
{
k
}
.
{
kk
}
"
                        
sections
[
section
]
=
vv
        
if
section
is
None
:
            
section
=
str
(
k
)
.
strip
(
"
'
\
"
"
)
            
sections
[
section
]
=
v
    
if
not
first_section
:
        
new_manifest
.
add
(
DEFAULT_SECTION
table
(
)
)
    
for
section
in
sort_paths
(
[
k
for
k
in
sections
.
keys
(
)
if
k
!
=
DEFAULT_SECTION
]
)
:
        
new_manifest
.
add
(
section
sections
[
section
]
)
    
manifest_str
=
dumps
(
new_manifest
)
    
#
tomlkit
fixups
    
manifest_str
=
preamble
+
manifest_str
.
replace
(
'
"
"
]
'
"
]
"
)
    
while
manifest_str
.
endswith
(
"
\
n
\
n
"
)
:
        
manifest_str
=
manifest_str
[
:
-
1
]
    
return
manifest_str
def
_simplify_comment
(
comment
)
:
    
"
"
"
Remove
any
leading
#
but
preserve
leading
whitespace
in
comment
"
"
"
    
if
comment
is
None
:
        
return
None
    
length
=
len
(
comment
)
    
i
=
0
    
j
=
-
1
#
remove
exactly
one
space
    
while
i
<
length
and
comment
[
i
]
in
"
#
"
:
        
i
+
=
1
        
if
comment
[
i
]
=
=
"
"
:
            
j
+
=
1
    
comment
=
comment
[
i
:
]
    
if
j
>
0
:
        
comment
=
"
"
*
j
+
comment
    
return
comment
.
rstrip
(
)
def
_should_keep_existing_condition
(
    
existing_condition
:
str
new_condition
:
str
)
-
>
bool
:
    
"
"
"
    
Checks
the
new
condition
is
equal
or
not
simpler
than
the
existing
one
    
"
"
"
    
return
(
        
existing_condition
=
=
new_condition
or
not
new_condition
in
existing_condition
    
)
def
_should_ignore_new_condition
(
existing_condition
:
str
new_condition
:
str
)
-
>
bool
:
    
"
"
"
    
Checks
if
the
new
condition
is
equal
or
more
complex
than
an
existing
one
    
"
"
"
    
return
existing_condition
=
=
new_condition
or
existing_condition
in
new_condition
class
Carry
:
    
"
Helper
class
for
add_skip_if
to
call
is_carryover
(
)
"
    
def
__init__
(
self
)
:
        
self
.
os_rx
:
Optional
[
re
.
Pattern
]
=
None
        
self
.
opt_rx
:
Optional
[
re
.
Pattern
]
=
None
        
self
.
not_opt_rx
:
Optional
[
re
.
Pattern
]
=
None
        
self
.
debug_rx
:
Optional
[
re
.
Pattern
]
=
None
        
self
.
not_debug_rx
:
Optional
[
re
.
Pattern
]
=
None
        
self
.
asan_rx
:
Optional
[
re
.
Pattern
]
=
None
        
self
.
tsan_rx
:
Optional
[
re
.
Pattern
]
=
None
        
self
.
ccov_rx
:
Optional
[
re
.
Pattern
]
=
None
        
self
.
text_index
:
int
=
0
#
to
facilitate
testing
only
    
def
test_index
(
self
)
-
>
int
:
        
"
Returns
expected
relative
index
number
of
next
test
"
        
self
.
text_index
+
=
1
        
return
self
.
text_index
    
def
initialize
(
self
)
:
        
if
self
.
opt_rx
is
None
:
            
self
.
os_rx
=
re
.
compile
(
r
"
os
=
=
[
'
\
"
]
(
[
a
-
z
]
+
)
[
'
\
"
]
"
)
            
#
pre
=
Either
start
of
string
^
            
#
Or
a
preceding
character
that
is
not
a
letter
digit
!
or
_
.
            
pre
=
r
"
(
?
:
(
?
<
!
[
A
-
Za
-
z0
-
9
!
_
]
)
|
^
)
"
            
#
post
=
Either
whitespace
            
#
Or
a
non
-
alphanumeric
non
-
underscore
character
            
#
Or
end
of
string
.
            
post
=
r
"
(
?
:
(
?
=
\
s
)
|
(
?
=
[
^
A
-
Za
-
z0
-
9_
]
)
|
)
"
            
self
.
opt_rx
=
re
.
compile
(
pre
+
"
opt
"
+
post
)
            
self
.
not_opt_rx
=
re
.
compile
(
pre
+
"
!
opt
"
+
post
)
            
self
.
debug_rx
=
re
.
compile
(
pre
+
"
debug
"
+
post
)
            
self
.
not_debug_rx
=
re
.
compile
(
pre
+
"
!
debug
"
+
post
)
            
self
.
asan_rx
=
re
.
compile
(
pre
+
"
asan
"
+
post
)
            
self
.
tsan_rx
=
re
.
compile
(
pre
+
"
tsan
"
+
post
)
            
self
.
ccov_rx
=
re
.
compile
(
pre
+
"
ccov
"
+
post
)
    
def
os
(
self
s
:
str
)
-
>
str
:
        
self
.
initialize
(
)
        
m
=
self
.
os_rx
.
search
(
s
)
        
if
m
is
not
None
:
            
return
m
[
0
]
        
return
"
"
    
def
opt
(
self
s
:
str
)
-
>
bool
:
        
self
.
initialize
(
)
        
return
bool
(
self
.
opt_rx
.
search
(
s
)
)
    
def
not_opt
(
self
s
:
str
)
-
>
bool
:
        
self
.
initialize
(
)
        
return
bool
(
self
.
not_opt_rx
.
search
(
s
)
)
    
def
debug
(
self
s
:
str
)
-
>
bool
:
        
self
.
initialize
(
)
        
return
bool
(
self
.
debug_rx
.
search
(
s
)
)
    
def
not_debug
(
self
s
:
str
)
-
>
bool
:
        
self
.
initialize
(
)
        
return
bool
(
self
.
not_debug_rx
.
search
(
s
)
)
    
def
asan
(
self
s
:
str
)
-
>
bool
:
        
self
.
initialize
(
)
        
return
bool
(
self
.
asan_rx
.
search
(
s
)
)
    
def
tsan
(
self
s
:
str
)
-
>
bool
:
        
self
.
initialize
(
)
        
return
bool
(
self
.
tsan_rx
.
search
(
s
)
)
    
def
ccov
(
self
s
:
str
)
-
>
bool
:
        
self
.
initialize
(
)
        
return
bool
(
self
.
ccov_rx
.
search
(
s
)
)
    
def
is_carryover
(
self
existing_condition
:
str
new_condition
:
str
)
-
>
bool
:
        
"
"
"
        
Checks
if
the
new
condition
is
is
a
carryover
from
the
existing
        
condition
.
See
.
/
test
/
SKIP
-
FAILS
.
txt
and
Bug
197161
        
"
"
"
        
self
.
initialize
(
)
        
#
Does
the
OS
match
?
        
e_os
:
str
=
self
.
os
(
existing_condition
)
        
os
:
str
=
self
.
os
(
new_condition
)
        
if
e_os
:
            
if
not
os
or
e_os
!
=
os
:
                
return
False
#
os
mismatch
        
e_opt
:
bool
=
self
.
opt
(
existing_condition
)
        
e_not_opt
:
bool
=
self
.
not_opt
(
existing_condition
)
        
e_debug
:
bool
=
self
.
debug
(
existing_condition
)
        
e_not_debug
:
bool
=
self
.
not_debug
(
existing_condition
)
        
e_asan
:
bool
=
self
.
asan
(
existing_condition
)
        
e_tsan
:
bool
=
self
.
tsan
(
existing_condition
)
        
e_ccov
:
bool
=
self
.
ccov
(
existing_condition
)
        
opt
:
bool
=
self
.
opt
(
new_condition
)
        
not_opt
:
bool
=
self
.
not_opt
(
new_condition
)
        
debug
:
bool
=
self
.
debug
(
new_condition
)
        
not_debug
:
bool
=
self
.
not_debug
(
new_condition
)
        
asan
:
bool
=
self
.
asan
(
new_condition
)
        
tsan
:
bool
=
self
.
tsan
(
new_condition
)
        
ccov
:
bool
=
self
.
ccov
(
new_condition
)
        
#
NOTE
:
the
sum
of
bool
in
Python
is
the
most
efficient
way
to
        
#
determine
how
many
vars
are
true
(
as
bool
is
represented
at
0
or
1
)
        
if
sum
(
#
existing_condition
has
NO
build
type
            
[
e_opt
e_not_opt
e_debug
e_not_debug
e_asan
e_tsan
e_ccov
]
        
)
=
=
0
and
(
e_os
and
os
and
e_os
=
=
os
)
:
            
return
True
#
build
type
not
present
and
os
explicit
match
        
if
(
e_opt
or
e_not_debug
)
and
(
opt
or
not_debug
)
:
            
return
True
#
both
optimized
        
if
(
e_debug
and
sum
(
[
asan
tsan
ccov
]
)
=
=
1
)
or
(
            
sum
(
[
e_asan
e_tsan
e_ccov
]
)
=
=
1
and
debug
        
)
:
            
return
False
#
debug
!
=
[
asan
tsan
ccov
]
        
if
(
#
both
conditions
have
a
compatible
build
type
            
sum
(
[
e_not_opt
e_debug
e_asan
e_tsan
e_ccov
]
)
=
=
1
            
and
sum
(
[
not_opt
debug
asan
tsan
ccov
]
)
=
=
1
        
)
:
            
return
True
        
return
False
def
add_skip_if
(
    
manifest
:
TOMLDocument
    
filename
:
str
    
condition
:
str
    
bug_reference
:
OptionalStr
=
None
    
create_bug_lambda
:
CreateBug
=
None
    
carryover_mode
:
bool
=
False
)
-
>
TupleStrBool
:
    
"
"
"
    
Will
take
a
TOMLkit
manifest
document
(
i
.
e
.
from
a
previous
invocation
    
of
read_toml
(
.
.
.
document
=
True
)
and
accessing
the
document
    
from
mp
.
source_documents
[
filename
]
)
and
mutate
it
    
in
sorted
order
by
section
(
i
.
e
.
test
file
name
taking
bug
ids
into
consideration
)
.
    
Determine
if
this
condition
is
a
carryover
(
see
.
/
test
/
SKIP
-
FAILS
.
txt
and
Bug
1971610
)
    
In
carryover_mode
only
consider
carryover
edits
(
do
not
create
bugs
)
    
Else
when
not
in
carryover_mode
and
create_bug_lambda
is
not
None
      
then
invoke
create_bug_lambda
to
create
new
bug
    
Returns
(
additional_comment
carryover
)
where
      
additional_comment
is
the
empty
string
(
used
in
other
manifest
add_skip_if
functions
)
      
carryover
is
True
if
this
condition
is
carried
over
from
an
existing
condition
    
"
"
"
    
from
tomlkit
import
array
    
from
tomlkit
.
items
import
Comment
String
Whitespace
    
carry
=
Carry
(
)
    
additional_comment
:
str
=
"
"
    
carryover
:
bool
=
False
#
not
carried
over
from
a
previous
skip
-
if
    
if
filename
not
in
manifest
:
        
raise
Exception
(
f
"
TOML
manifest
does
not
contain
section
:
{
filename
}
"
)
    
keyvals
:
dict
=
manifest
[
filename
]
    
first
:
OptionalStr
=
None
    
first_comment
:
str
=
"
"
    
skip_if
:
Optional
[
Array
]
=
None
    
ignore_condition
:
bool
=
False
#
this
condition
should
not
be
added
    
if
"
skip
-
if
"
in
keyvals
:
        
skip_if
=
keyvals
[
"
skip
-
if
"
]
        
if
len
(
skip_if
)
=
=
1
:
            
for
e
in
skip_if
.
_iter_items
(
)
:
                
if
not
first
:
                    
if
not
isinstance
(
e
Whitespace
)
:
                        
first
=
e
.
as_string
(
)
.
strip
(
'
"
'
)
                
else
:
                    
c
=
e
.
as_string
(
)
                    
if
c
!
=
"
"
:
                        
first_comment
+
=
c
            
if
skip_if
.
trivia
is
not
None
:
                
first_comment
+
=
skip_if
.
trivia
.
comment
    
mp_array
:
Array
=
array
(
)
    
if
skip_if
is
None
:
#
add
the
first
one
line
entry
to
the
table
        
if
not
carryover_mode
:
            
mp_array
.
add_line
(
condition
indent
=
"
"
add_comma
=
False
newline
=
False
)
            
if
create_bug_lambda
is
not
None
:
                
bug
=
create_bug_lambda
(
)
                
if
bug
is
not
None
:
                    
bug_reference
=
f
"
Bug
{
bug
.
id
}
"
            
if
bug_reference
is
not
None
:
                
mp_array
.
comment
(
bug_reference
)
            
skip_if
=
{
"
skip
-
if
"
:
mp_array
}
            
keyvals
.
update
(
skip_if
)
    
else
:
        
#
We
store
the
conditions
in
a
regular
python
array
so
we
can
sort
them
before
        
#
dumping
them
in
the
TOML
        
conditions_array
:
list
=
[
]
        
if
first
is
not
None
:
            
if
_should_ignore_new_condition
(
first
condition
)
:
                
ignore_condition
=
True
            
if
first_comment
:
                
first_comment
=
_simplify_comment
(
first_comment
)
            
if
_should_keep_existing_condition
(
first
condition
)
:
                
conditions_array
.
append
(
[
first
first_comment
]
)
                
if
(
                    
not
ignore_condition
                    
and
carryover_mode
                    
and
carry
.
is_carryover
(
first
condition
)
                
)
:
                    
carryover
=
True
                    
bug_reference
=
first_comment
            
elif
bug_reference
is
None
and
create_bug_lambda
is
None
:
                
bug_reference
=
first_comment
        
if
len
(
skip_if
)
>
1
:
            
e_condition
=
None
            
e_comment
=
None
            
for
e
in
skip_if
.
_iter_items
(
)
:
                
if
isinstance
(
e
String
)
:
                    
if
e_condition
is
not
None
:
                        
if
_should_keep_existing_condition
(
e_condition
condition
)
:
                            
conditions_array
.
append
(
[
e_condition
e_comment
]
)
                            
if
(
                                
not
ignore_condition
                                
and
carryover_mode
                                
and
carry
.
is_carryover
(
e_condition
condition
)
                            
)
:
                                
carryover
=
True
                                
bug_reference
=
e_comment
                        
elif
bug_reference
is
None
and
create_bug_lambda
is
None
:
                            
bug_reference
=
e_comment
                        
e_comment
=
None
                        
e_condition
=
None
                    
if
len
(
e
)
>
0
:
                        
e_condition
=
e
.
as_string
(
)
.
strip
(
'
"
'
)
                        
if
_should_ignore_new_condition
(
e_condition
condition
)
:
                            
ignore_condition
=
True
                
elif
isinstance
(
e
Comment
)
:
                    
e_comment
=
_simplify_comment
(
e
.
as_string
(
)
)
            
if
e_condition
is
not
None
:
                
if
_should_keep_existing_condition
(
e_condition
condition
)
:
                    
conditions_array
.
append
(
[
e_condition
e_comment
]
)
                    
if
(
                        
not
ignore_condition
                        
and
carryover_mode
                        
and
carry
.
is_carryover
(
e_condition
condition
)
                    
)
:
                        
carryover
=
True
                        
bug_reference
=
e_comment
                
elif
bug_reference
is
None
and
create_bug_lambda
is
None
:
                    
bug_reference
=
e_comment
        
if
not
ignore_condition
:
            
if
not
carryover_mode
and
create_bug_lambda
is
not
None
:
                
bug
=
create_bug_lambda
(
)
                
if
bug
is
not
None
:
                    
bug_reference
=
f
"
Bug
{
bug
.
id
}
"
            
conditions_array
.
append
(
[
condition
bug_reference
]
)
        
conditions_array
.
sort
(
)
        
for
c
in
conditions_array
:
            
mp_array
.
add_line
(
c
[
0
]
indent
=
"
"
comment
=
c
[
1
]
)
        
mp_array
.
add_line
(
"
"
indent
=
"
"
)
#
fixed
in
write_toml_str
        
skip_if
=
{
"
skip
-
if
"
:
mp_array
}
        
del
keyvals
[
"
skip
-
if
"
]
        
keyvals
.
update
(
skip_if
)
    
return
(
additional_comment
carryover
)
def
_should_remove_condition
(
    
condition
:
str
    
os_name
:
Optional
[
str
]
=
None
    
os_version
:
Optional
[
str
]
=
None
    
processor
:
Optional
[
str
]
=
None
)
:
    
to_ignore
=
[
os_name
os_version
processor
]
    
for
part
in
to_ignore
:
        
if
part
is
not
None
and
part
not
in
condition
:
            
return
False
    
return
True
def
remove_skip_if
(
    
manifest
:
TOMLDocument
    
os_name
:
Optional
[
str
]
=
None
    
os_version
:
Optional
[
str
]
=
None
    
processor
:
Optional
[
str
]
=
None
)
:
    
from
tomlkit
import
array
    
from
tomlkit
.
items
import
Comment
String
    
if
os_name
is
None
and
os_version
is
None
and
processor
is
None
:
        
raise
ValueError
(
"
Needs
at
least
os
name
version
or
processor
to
be
set
.
"
)
    
has_removed_items
=
False
    
for
filename
in
manifest
:
        
key_values
=
manifest
[
filename
]
        
if
isinstance
(
key_values
Table
)
and
"
skip
-
if
"
in
key_values
:
            
condition_array
=
key_values
[
"
skip
-
if
"
]
            
if
isinstance
(
condition_array
Array
)
:
                
new_conditions
=
array
(
)
                
condition
=
None
                
comment
=
None
                
conditions_to_add
:
list
[
tuple
[
str
Optional
[
str
]
]
]
=
[
]
                
for
item
in
condition_array
.
_iter_items
(
)
:
                    
if
isinstance
(
item
String
)
:
                        
if
condition
is
not
None
:
                            
if
not
_should_remove_condition
(
                                
condition
os_name
os_version
processor
                            
)
:
                                
conditions_to_add
.
append
(
(
condition
comment
)
)
                            
else
:
                                
has_removed_items
=
True
                            
condition
=
None
                            
comment
=
None
                        
if
len
(
item
)
>
0
:
                            
condition
=
item
.
as_string
(
)
.
strip
(
'
"
'
)
                    
elif
isinstance
(
item
Comment
)
:
                        
comment
=
_simplify_comment
(
item
.
as_string
(
)
)
                
if
condition
is
not
None
:
                    
if
not
_should_remove_condition
(
                        
condition
os_name
os_version
processor
                    
)
:
                        
conditions_to_add
.
append
(
(
condition
comment
)
)
                    
else
:
                        
has_removed_items
=
True
                
if
len
(
conditions_to_add
)
>
0
:
                    
#
If
there
is
only
one
condition
make
the
skip
-
if
a
one
-
liner
                    
if
len
(
conditions_to_add
)
>
1
:
                        
for
condition
comment
in
conditions_to_add
:
                            
new_conditions
.
add_line
(
                                
condition
comment
=
comment
indent
=
"
"
                            
)
                    
else
:
                        
condition
comment
=
conditions_to_add
[
0
]
                        
new_conditions
.
add_line
(
                            
condition
indent
=
"
"
add_comma
=
False
newline
=
False
                        
)
                        
#
Make
sure
the
comment
is
added
outside
the
array
on
one
-
liners
                        
if
comment
is
not
None
:
                            
new_conditions
.
comment
(
comment
)
                
#
Do
not
keep
an
empty
skip
-
if
array
if
there
are
no
conditions
                
if
len
(
new_conditions
)
>
0
:
                    
if
len
(
new_conditions
)
>
1
:
                        
new_conditions
.
add_line
(
"
"
indent
=
"
"
)
                    
key_values
.
update
(
{
"
skip
-
if
"
:
new_conditions
}
)
                
else
:
                    
del
key_values
[
"
skip
-
if
"
]
    
return
has_removed_items
