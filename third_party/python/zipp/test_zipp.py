import
io
import
zipfile
import
contextlib
import
pathlib
import
unittest
import
tempfile
import
shutil
import
string
import
functools
import
jaraco
.
itertools
import
func_timeout
import
zipp
consume
=
tuple
def
add_dirs
(
zf
)
:
    
"
"
"
    
Given
a
writable
zip
file
zf
inject
directory
entries
for
    
any
directories
implied
by
the
presence
of
children
.
    
"
"
"
    
for
name
in
zipp
.
CompleteDirs
.
_implied_dirs
(
zf
.
namelist
(
)
)
:
        
zf
.
writestr
(
name
b
"
"
)
    
return
zf
def
build_alpharep_fixture
(
)
:
    
"
"
"
    
Create
a
zip
file
with
this
structure
:
    
.
    
a
.
txt
    
b
    
c
.
txt
    
d
    
e
.
txt
    
f
.
txt
    
g
        
h
            
i
.
txt
    
This
fixture
has
the
following
key
characteristics
:
    
-
a
file
at
the
root
(
a
)
    
-
a
file
two
levels
deep
(
b
/
d
/
e
)
    
-
multiple
files
in
a
directory
(
b
/
c
b
/
f
)
    
-
a
directory
containing
only
a
directory
(
g
/
h
)
    
"
alpha
"
because
it
uses
alphabet
    
"
rep
"
because
it
'
s
a
representative
example
    
"
"
"
    
data
=
io
.
BytesIO
(
)
    
zf
=
zipfile
.
ZipFile
(
data
"
w
"
)
    
zf
.
writestr
(
"
a
.
txt
"
b
"
content
of
a
"
)
    
zf
.
writestr
(
"
b
/
c
.
txt
"
b
"
content
of
c
"
)
    
zf
.
writestr
(
"
b
/
d
/
e
.
txt
"
b
"
content
of
e
"
)
    
zf
.
writestr
(
"
b
/
f
.
txt
"
b
"
content
of
f
"
)
    
zf
.
writestr
(
"
g
/
h
/
i
.
txt
"
b
"
content
of
i
"
)
    
zf
.
filename
=
"
alpharep
.
zip
"
    
return
zf
contextlib
.
contextmanager
def
temp_dir
(
)
:
    
tmpdir
=
tempfile
.
mkdtemp
(
)
    
try
:
        
yield
pathlib
.
Path
(
tmpdir
)
    
finally
:
        
shutil
.
rmtree
(
tmpdir
)
def
pass_alpharep
(
meth
)
:
    
"
"
"
    
Given
a
method
wrap
it
in
a
for
loop
that
invokes
method
    
with
each
subtest
.
    
"
"
"
    
functools
.
wraps
(
meth
)
    
def
wrapper
(
self
)
:
        
for
alpharep
in
self
.
zipfile_alpharep
(
)
:
            
meth
(
self
alpharep
=
alpharep
)
    
return
wrapper
class
TestPath
(
unittest
.
TestCase
)
:
    
def
setUp
(
self
)
:
        
self
.
fixtures
=
contextlib
.
ExitStack
(
)
        
self
.
addCleanup
(
self
.
fixtures
.
close
)
    
def
zipfile_alpharep
(
self
)
:
        
with
self
.
subTest
(
)
:
            
yield
build_alpharep_fixture
(
)
        
with
self
.
subTest
(
)
:
            
yield
add_dirs
(
build_alpharep_fixture
(
)
)
    
def
zipfile_ondisk
(
self
alpharep
)
:
        
tmpdir
=
pathlib
.
Path
(
self
.
fixtures
.
enter_context
(
temp_dir
(
)
)
)
        
buffer
=
alpharep
.
fp
        
alpharep
.
close
(
)
        
path
=
tmpdir
/
alpharep
.
filename
        
with
path
.
open
(
"
wb
"
)
as
strm
:
            
strm
.
write
(
buffer
.
getvalue
(
)
)
        
return
path
    
pass_alpharep
    
def
test_iterdir_and_types
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
assert
root
.
is_dir
(
)
        
a
b
g
=
root
.
iterdir
(
)
        
assert
a
.
is_file
(
)
        
assert
b
.
is_dir
(
)
        
assert
g
.
is_dir
(
)
        
c
f
d
=
b
.
iterdir
(
)
        
assert
c
.
is_file
(
)
and
f
.
is_file
(
)
        
(
e
)
=
d
.
iterdir
(
)
        
assert
e
.
is_file
(
)
        
(
h
)
=
g
.
iterdir
(
)
        
(
i
)
=
h
.
iterdir
(
)
        
assert
i
.
is_file
(
)
    
pass_alpharep
    
def
test_is_file_missing
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
assert
not
root
.
joinpath
(
'
missing
.
txt
'
)
.
is_file
(
)
    
pass_alpharep
    
def
test_iterdir_on_file
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
a
b
g
=
root
.
iterdir
(
)
        
with
self
.
assertRaises
(
ValueError
)
:
            
a
.
iterdir
(
)
    
pass_alpharep
    
def
test_subdir_is_dir
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
assert
(
root
/
'
b
'
)
.
is_dir
(
)
        
assert
(
root
/
'
b
/
'
)
.
is_dir
(
)
        
assert
(
root
/
'
g
'
)
.
is_dir
(
)
        
assert
(
root
/
'
g
/
'
)
.
is_dir
(
)
    
pass_alpharep
    
def
test_open
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
a
b
g
=
root
.
iterdir
(
)
        
with
a
.
open
(
)
as
strm
:
            
data
=
strm
.
read
(
)
        
assert
data
=
=
"
content
of
a
"
    
def
test_open_write
(
self
)
:
        
"
"
"
        
If
the
zipfile
is
open
for
write
it
should
be
possible
to
        
write
bytes
or
text
to
it
.
        
"
"
"
        
zf
=
zipp
.
Path
(
zipfile
.
ZipFile
(
io
.
BytesIO
(
)
mode
=
'
w
'
)
)
        
with
zf
.
joinpath
(
'
file
.
bin
'
)
.
open
(
'
wb
'
)
as
strm
:
            
strm
.
write
(
b
'
binary
contents
'
)
        
with
zf
.
joinpath
(
'
file
.
txt
'
)
.
open
(
'
w
'
)
as
strm
:
            
strm
.
write
(
'
text
file
'
)
    
def
test_open_extant_directory
(
self
)
:
        
"
"
"
        
Attempting
to
open
a
directory
raises
IsADirectoryError
.
        
"
"
"
        
zf
=
zipp
.
Path
(
add_dirs
(
build_alpharep_fixture
(
)
)
)
        
with
self
.
assertRaises
(
IsADirectoryError
)
:
            
zf
.
joinpath
(
'
b
'
)
.
open
(
)
    
pass_alpharep
    
def
test_open_binary_invalid_args
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
with
self
.
assertRaises
(
ValueError
)
:
            
root
.
joinpath
(
'
a
.
txt
'
)
.
open
(
'
rb
'
encoding
=
'
utf
-
8
'
)
        
with
self
.
assertRaises
(
ValueError
)
:
            
root
.
joinpath
(
'
a
.
txt
'
)
.
open
(
'
rb
'
'
utf
-
8
'
)
    
def
test_open_missing_directory
(
self
)
:
        
"
"
"
        
Attempting
to
open
a
missing
directory
raises
FileNotFoundError
.
        
"
"
"
        
zf
=
zipp
.
Path
(
add_dirs
(
build_alpharep_fixture
(
)
)
)
        
with
self
.
assertRaises
(
FileNotFoundError
)
:
            
zf
.
joinpath
(
'
z
'
)
.
open
(
)
    
pass_alpharep
    
def
test_read
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
a
b
g
=
root
.
iterdir
(
)
        
assert
a
.
read_text
(
)
=
=
"
content
of
a
"
        
assert
a
.
read_bytes
(
)
=
=
b
"
content
of
a
"
    
pass_alpharep
    
def
test_joinpath
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
a
=
root
.
joinpath
(
"
a
.
txt
"
)
        
assert
a
.
is_file
(
)
        
e
=
root
.
joinpath
(
"
b
"
)
.
joinpath
(
"
d
"
)
.
joinpath
(
"
e
.
txt
"
)
        
assert
e
.
read_text
(
)
=
=
"
content
of
e
"
    
pass_alpharep
    
def
test_joinpath_multiple
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
e
=
root
.
joinpath
(
"
b
"
"
d
"
"
e
.
txt
"
)
        
assert
e
.
read_text
(
)
=
=
"
content
of
e
"
    
pass_alpharep
    
def
test_traverse_truediv
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
a
=
root
/
"
a
.
txt
"
        
assert
a
.
is_file
(
)
        
e
=
root
/
"
b
"
/
"
d
"
/
"
e
.
txt
"
        
assert
e
.
read_text
(
)
=
=
"
content
of
e
"
    
pass_alpharep
    
def
test_traverse_simplediv
(
self
alpharep
)
:
        
"
"
"
        
Disable
the
__future__
.
division
when
testing
traversal
.
        
"
"
"
        
code
=
compile
(
            
source
=
"
zipp
.
Path
(
alpharep
)
/
'
a
'
"
            
filename
=
"
(
test
)
"
            
mode
=
"
eval
"
            
dont_inherit
=
True
        
)
        
eval
(
code
)
    
pass_alpharep
    
def
test_pathlike_construction
(
self
alpharep
)
:
        
"
"
"
        
zipp
.
Path
should
be
constructable
from
a
path
-
like
object
        
"
"
"
        
zipfile_ondisk
=
self
.
zipfile_ondisk
(
alpharep
)
        
pathlike
=
pathlib
.
Path
(
str
(
zipfile_ondisk
)
)
        
zipp
.
Path
(
pathlike
)
    
pass_alpharep
    
def
test_traverse_pathlike
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
root
/
pathlib
.
Path
(
"
a
"
)
    
pass_alpharep
    
def
test_parent
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
assert
(
root
/
'
a
'
)
.
parent
.
at
=
=
'
'
        
assert
(
root
/
'
a
'
/
'
b
'
)
.
parent
.
at
=
=
'
a
/
'
    
pass_alpharep
    
def
test_dir_parent
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
assert
(
root
/
'
b
'
)
.
parent
.
at
=
=
'
'
        
assert
(
root
/
'
b
/
'
)
.
parent
.
at
=
=
'
'
    
pass_alpharep
    
def
test_missing_dir_parent
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
assert
(
root
/
'
missing
dir
/
'
)
.
parent
.
at
=
=
'
'
    
pass_alpharep
    
def
test_mutability
(
self
alpharep
)
:
        
"
"
"
        
If
the
underlying
zipfile
is
changed
the
Path
object
should
        
reflect
that
change
.
        
"
"
"
        
root
=
zipp
.
Path
(
alpharep
)
        
a
b
g
=
root
.
iterdir
(
)
        
alpharep
.
writestr
(
'
foo
.
txt
'
'
foo
'
)
        
alpharep
.
writestr
(
'
bar
/
baz
.
txt
'
'
baz
'
)
        
assert
any
(
child
.
name
=
=
'
foo
.
txt
'
for
child
in
root
.
iterdir
(
)
)
        
assert
(
root
/
'
foo
.
txt
'
)
.
read_text
(
)
=
=
'
foo
'
        
(
baz
)
=
(
root
/
'
bar
'
)
.
iterdir
(
)
        
assert
baz
.
read_text
(
)
=
=
'
baz
'
    
HUGE_ZIPFILE_NUM_ENTRIES
=
2
*
*
13
    
def
huge_zipfile
(
self
)
:
        
"
"
"
Create
a
read
-
only
zipfile
with
a
huge
number
of
entries
entries
.
"
"
"
        
strm
=
io
.
BytesIO
(
)
        
zf
=
zipfile
.
ZipFile
(
strm
"
w
"
)
        
for
entry
in
map
(
str
range
(
self
.
HUGE_ZIPFILE_NUM_ENTRIES
)
)
:
            
zf
.
writestr
(
entry
entry
)
        
zf
.
mode
=
'
r
'
        
return
zf
    
def
test_joinpath_constant_time
(
self
)
:
        
"
"
"
        
Ensure
joinpath
on
items
in
zipfile
is
linear
time
.
        
"
"
"
        
root
=
zipp
.
Path
(
self
.
huge_zipfile
(
)
)
        
entries
=
jaraco
.
itertools
.
Counter
(
root
.
iterdir
(
)
)
        
for
entry
in
entries
:
            
entry
.
joinpath
(
'
suffix
'
)
        
#
Check
the
file
iterated
all
items
        
assert
entries
.
count
=
=
self
.
HUGE_ZIPFILE_NUM_ENTRIES
    
func_timeout
.
func_set_timeout
(
3
)
    
def
test_implied_dirs_performance
(
self
)
:
        
data
=
[
'
/
'
.
join
(
string
.
ascii_lowercase
+
str
(
n
)
)
for
n
in
range
(
10000
)
]
        
zipp
.
CompleteDirs
.
_implied_dirs
(
data
)
    
pass_alpharep
    
def
test_read_does_not_close
(
self
alpharep
)
:
        
alpharep
=
self
.
zipfile_ondisk
(
alpharep
)
        
with
zipfile
.
ZipFile
(
alpharep
)
as
file
:
            
for
rep
in
range
(
2
)
:
                
zipp
.
Path
(
file
'
a
.
txt
'
)
.
read_text
(
)
    
pass_alpharep
    
def
test_subclass
(
self
alpharep
)
:
        
class
Subclass
(
zipp
.
Path
)
:
            
pass
        
root
=
Subclass
(
alpharep
)
        
assert
isinstance
(
root
/
'
b
'
Subclass
)
    
pass_alpharep
    
def
test_filename
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
assert
root
.
filename
=
=
pathlib
.
Path
(
'
alpharep
.
zip
'
)
    
pass_alpharep
    
def
test_root_name
(
self
alpharep
)
:
        
"
"
"
        
The
name
of
the
root
should
be
the
name
of
the
zipfile
        
"
"
"
        
root
=
zipp
.
Path
(
alpharep
)
        
assert
root
.
name
=
=
'
alpharep
.
zip
'
=
=
root
.
filename
.
name
    
pass_alpharep
    
def
test_root_parent
(
self
alpharep
)
:
        
root
=
zipp
.
Path
(
alpharep
)
        
assert
root
.
parent
=
=
pathlib
.
Path
(
'
.
'
)
        
root
.
root
.
filename
=
'
foo
/
bar
.
zip
'
        
assert
root
.
parent
=
=
pathlib
.
Path
(
'
foo
'
)
    
pass_alpharep
    
def
test_root_unnamed
(
self
alpharep
)
:
        
"
"
"
        
It
is
an
error
to
attempt
to
get
the
name
        
or
parent
of
an
unnamed
zipfile
.
        
"
"
"
        
alpharep
.
filename
=
None
        
root
=
zipp
.
Path
(
alpharep
)
        
with
self
.
assertRaises
(
TypeError
)
:
            
root
.
name
        
with
self
.
assertRaises
(
TypeError
)
:
            
root
.
parent
        
#
.
name
and
.
parent
should
still
work
on
subs
        
sub
=
root
/
"
b
"
        
assert
sub
.
name
=
=
"
b
"
        
assert
sub
.
parent
    
pass_alpharep
    
def
test_inheritance
(
self
alpharep
)
:
        
cls
=
type
(
'
PathChild
'
(
zipp
.
Path
)
{
}
)
        
for
alpharep
in
self
.
zipfile_alpharep
(
)
:
            
file
=
cls
(
alpharep
)
.
joinpath
(
'
some
dir
'
)
.
parent
            
assert
isinstance
(
file
cls
)
