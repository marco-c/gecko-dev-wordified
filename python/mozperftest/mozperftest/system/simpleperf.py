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
#
file
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
shutil
import
signal
import
subprocess
import
tarfile
import
tempfile
import
time
import
zipfile
from
pathlib
import
Path
from
urllib
.
parse
import
unquote
from
mozbuild
.
nodeutil
import
find_node_executable
from
mozdevice
import
ADBDevice
from
mozperftest
.
layers
import
Layer
from
mozperftest
.
utils
import
ON_TRY
"
"
"
The
default
Simpleperf
options
will
collect
a
30s
system
-
wide
profile
that
uses
DWARF
based
   
call
graph
so
that
we
can
collect
Java
stacks
.
This
requires
root
access
.
"
"
"
DEFAULT_SIMPLEPERF_OPTS
=
"
-
g
-
-
duration
30
-
f
1000
-
-
trace
-
offcpu
-
e
cpu
-
clock
-
a
"
BREAKPAD_SYMBOL_SERVER
=
"
https
:
/
/
symbols
.
mozilla
.
org
/
"
SYMBOL_SERVER_TIMEOUT
=
60
#
seconds
class
SimpleperfError
(
Exception
)
:
    
"
"
"
Base
class
for
Simpleperf
-
related
exceptions
.
"
"
"
    
pass
class
SimpleperfAlreadyRunningError
(
SimpleperfError
)
:
    
"
"
"
Raised
when
attempting
to
start
simpleperf
while
it
'
s
already
running
.
"
"
"
    
pass
class
SimpleperfNotRunningError
(
SimpleperfError
)
:
    
"
"
"
Raised
when
attempting
to
stop
simpleperf
when
it
'
s
not
running
.
"
"
"
    
pass
class
SimpleperfExecutionError
(
SimpleperfError
)
:
    
"
"
"
Raised
when
simpleperf
fails
to
execute
properly
.
"
"
"
    
pass
class
SimpleperfSystemError
(
SimpleperfError
)
:
    
"
"
"
Raised
when
the
system
is
not
compatible
with
Android
NDK
installation
.
"
"
"
    
pass
class
SimpleperfBinaryNotFoundError
(
SimpleperfError
)
:
    
"
"
"
Raised
when
the
simpleperf
binary
cannot
be
found
at
the
expected
path
.
"
"
"
    
pass
class
SimpleperfSymbolicationTimeoutError
(
SimpleperfError
)
:
    
"
"
"
Raised
when
starting
the
samply
server
required
for
symbolicating
    
simpleperf
profiles
execeeds
the
specified
time
time
limit
.
"
"
"
    
pass
class
SimpleperfSymbolicationError
(
SimpleperfError
)
:
    
"
"
"
Raised
when
symbolication
paths
are
missing
or
invalid
.
"
"
"
    
pass
class
SimpleperfController
:
    
def
__init__
(
self
)
:
        
self
.
device
=
ADBDevice
(
)
        
self
.
profiler_process
=
None
    
def
start
(
self
simpleperf_opts
)
:
        
"
"
"
Starts
the
simpleperf
profiler
asynchronously
if
the
layer
is
enabled
.
        
This
method
expects
that
the
/
data
/
local
/
tmp
/
simpleperf
binary
has
        
already
been
installed
during
the
setup
phase
of
the
layer
.
        
The
simpleperf
options
can
be
provided
as
an
argument
.
If
none
are
        
provided
we
default
to
system
-
wide
profiling
which
will
require
        
root
access
.
        
"
"
"
        
if
simpleperf_opts
is
None
:
            
simpleperf_opts
=
DEFAULT_SIMPLEPERF_OPTS
        
assert
SimpleperfProfiler
.
is_enabled
(
)
        
if
self
.
profiler_process
:
            
raise
SimpleperfAlreadyRunningError
(
"
simpleperf
already
running
"
)
        
cmd
=
f
"
/
data
/
local
/
tmp
/
simpleperf
record
{
simpleperf_opts
}
-
o
/
data
/
local
/
tmp
/
perf
.
data
"
        
self
.
profiler_process
=
subprocess
.
Popen
(
            
[
                
"
adb
"
                
"
shell
"
                
"
su
"
                
"
-
c
"
                
cmd
            
]
            
stdout
=
subprocess
.
PIPE
            
stderr
=
subprocess
.
PIPE
        
)
        
#
Sleep
for
1s
to
let
simpleperf
settle
and
begin
profiling
.
        
time
.
sleep
(
1
)
    
def
stop
(
self
output_path
index
)
:
        
assert
SimpleperfProfiler
.
is_enabled
(
)
        
if
not
self
.
profiler_process
:
            
raise
SimpleperfNotRunningError
(
"
no
profiler
process
found
"
)
        
#
Send
SIGINT
to
simpleperf
on
the
device
to
stop
profiling
.
        
self
.
device
.
shell
(
"
kill
(
pgrep
simpleperf
)
"
)
        
stdout_data
stderr_data
=
self
.
profiler_process
.
communicate
(
)
        
if
self
.
profiler_process
.
returncode
!
=
0
:
            
print
(
"
Error
running
simpleperf
"
)
            
print
(
"
output
:
"
stderr_data
.
decode
(
)
)
            
raise
SimpleperfExecutionError
(
"
failed
to
run
simpleperf
"
)
        
self
.
profiler_process
=
None
        
output_path
=
str
(
Path
(
output_path
f
"
perf
-
{
index
}
.
data
"
)
)
        
#
Pull
profiler
data
directly
to
the
given
output
path
.
        
self
.
device
.
pull
(
"
/
data
/
local
/
tmp
/
perf
.
data
"
output_path
)
        
self
.
device
.
shell
(
"
rm
-
f
/
data
/
local
/
tmp
/
perf
.
data
"
)
class
SimpleperfProfiler
(
Layer
)
:
    
name
=
"
simpleperf
"
    
activated
=
False
    
arguments
=
{
        
"
path
"
:
{
            
"
type
"
:
str
            
"
default
"
:
None
            
"
help
"
:
"
Path
to
the
Simpleperf
NDK
.
"
        
}
        
"
symbol
-
path
"
:
{
            
"
type
"
:
str
            
"
default
"
:
None
            
"
help
"
:
"
Path
to
breakpad
symbols
directory
(
e
.
g
.
target
.
crashreporter
-
symbols
)
.
"
        
}
        
"
symbolicator
-
path
"
:
{
            
"
type
"
:
str
            
"
default
"
:
None
            
"
help
"
:
"
Path
to
directory
containing
symbolicator
-
cli
build
.
"
        
}
    
}
    
def
__init__
(
self
env
mach_cmd
)
:
        
super
(
SimpleperfProfiler
self
)
.
__init__
(
env
mach_cmd
)
        
self
.
device
=
ADBDevice
(
)
    
staticmethod
    
def
is_enabled
(
)
:
        
return
os
.
environ
.
get
(
"
MOZPERFTEST_SIMPLEPERF
"
"
0
"
)
=
=
"
1
"
    
staticmethod
    
def
get_controller
(
)
:
        
return
SimpleperfController
(
)
    
def
setup_simpleperf_path
(
self
)
:
        
"
"
"
Sets
up
and
verifies
that
the
simpleperf
NDK
exists
.
        
If
no
simpleperf
path
is
provided
this
step
will
try
to
install
        
the
Android
NDK
locally
.
        
"
"
"
        
if
self
.
get_arg
(
"
path
"
None
)
is
None
:
            
import
platform
            
from
mozboot
import
android
            
os_name
=
None
            
if
platform
.
system
(
)
=
=
"
Windows
"
:
                
os_name
=
"
windows
"
            
elif
platform
.
system
(
)
=
=
"
Linux
"
:
                
os_name
=
"
linux
"
            
elif
platform
.
system
(
)
=
=
"
Darwin
"
:
                
os_name
=
"
mac
"
            
else
:
                
raise
SimpleperfSystemError
(
                    
"
Unknown
system
in
order
to
install
Android
NDK
"
                
)
            
android
.
ensure_android_ndk
(
os_name
)
            
self
.
set_arg
(
"
path
"
str
(
Path
(
android
.
NDK_PATH
"
simpleperf
"
)
)
)
        
#
Make
sure
the
arm64
binary
exists
in
the
NDK
path
.
        
binary_path
=
Path
(
            
self
.
get_arg
(
"
path
"
)
"
bin
"
"
android
"
"
arm64
"
"
simpleperf
"
        
)
        
if
not
os
.
path
.
exists
(
binary_path
)
:
            
raise
SimpleperfBinaryNotFoundError
(
                
f
"
Cannot
find
simpleperf
binary
at
{
binary_path
}
"
            
)
    
def
_cleanup
(
self
)
:
        
"
"
"
Cleanup
step
called
during
setup
and
teardown
.
        
Remove
any
leftover
profiles
and
simpleperf
binaries
on
the
device
        
and
also
undefine
the
MOZPERFTEST_SIMPLEPERF
environment
variable
.
        
"
"
"
        
self
.
device
.
shell
(
"
rm
-
f
/
data
/
local
/
tmp
/
perf
.
data
/
data
/
local
/
tmp
/
simpleperf
"
)
        
os
.
environ
.
pop
(
"
MOZPERFTEST_SIMPLEPERF
"
None
)
    
def
setup
(
self
)
:
        
"
"
"
Setup
the
simpleperf
layer
        
First
verify
that
the
simpleperf
NDK
and
ARM64
binary
exists
.
        
Next
install
the
ARM64
simpleperf
binary
in
/
data
/
local
/
tmp
on
the
device
.
        
Finally
define
MOZPERFTEST_SIMPLEPERF
to
indicate
layer
is
active
.
        
"
"
"
        
self
.
setup_simpleperf_path
(
)
        
self
.
_cleanup
(
)
        
self
.
device
.
push
(
            
Path
(
self
.
get_arg
(
"
path
"
)
"
bin
"
"
android
"
"
arm64
"
"
simpleperf
"
)
            
"
/
data
/
local
/
tmp
"
        
)
        
self
.
device
.
shell
(
"
chmod
a
+
x
/
data
/
local
/
tmp
/
simpleperf
"
)
        
os
.
environ
[
"
MOZPERFTEST_SIMPLEPERF
"
]
=
"
1
"
    
def
_validate_symbolication_paths
(
self
symbol_dir_arg
symbolicator_dir_arg
)
:
        
"
"
"
Check
if
the
breakpad
directory
path
and
the
symbolicator
-
cli
paths
        
for
symbolication
are
valid
.
        
:
param
symbol_dir_arg
str
:
Path
to
the
Breakpad
symbol
directory
        
:
param
symbolicator_dir_arg
str
:
Path
to
the
symbolicator
-
cli
directory
        
:
return
tuple
[
pathlib
.
Path
pathlib
.
Path
]
:
Returns
a
tuple
containing
validated
(
breakpad_symbol_dir
symbolicator_dir
)
.
        
:
raises
SimpleperfSymbolicationError
:
If
validation
fails
        
"
"
"
        
if
not
symbol_dir_arg
:
            
raise
SimpleperfSymbolicationError
(
                
"
Breakpad
Symbol
Directory
not
provided
.
"
            
)
        
breakpad_symbol_dir
=
Path
(
symbol_dir_arg
)
        
if
not
breakpad_symbol_dir
.
exists
(
)
:
            
raise
SimpleperfSymbolicationError
(
                
f
"
Breakpad
Symbol
Directory
not
found
at
{
breakpad_symbol_dir
}
.
"
            
)
        
if
not
symbolicator_dir_arg
:
            
raise
SimpleperfSymbolicationError
(
"
Symbolicator
Directory
not
provided
.
"
)
        
symbolicator_dir
=
Path
(
symbolicator_dir_arg
)
        
if
not
symbolicator_dir
.
exists
(
)
:
            
raise
SimpleperfSymbolicationError
(
                
f
"
Symbolicator
Directory
not
found
at
{
symbolicator_dir
}
.
"
            
)
        
return
breakpad_symbol_dir
symbolicator_dir
    
def
_prepare_symbolication_environment
(
self
)
:
        
"
"
"
Set
up
variables
needed
by
symbolication
helper
functions
.
        
:
return
bool
:
Returns
True
if
preparation
is
successful
False
otherwise
.
        
"
"
"
        
self
.
output_dir
=
self
.
get_arg
(
"
output
"
)
        
self
.
work_dir
=
Path
(
tempfile
.
mkdtemp
(
)
)
        
if
ON_TRY
:
            
moz_fetch
=
os
.
environ
[
"
MOZ_FETCHES_DIR
"
]
            
self
.
breakpad_symbol_dir
=
Path
(
moz_fetch
"
target
.
crashreporter
-
symbols
"
)
            
self
.
samply_path
=
Path
(
moz_fetch
"
samply
"
"
samply
"
)
            
self
.
node_path
=
Path
(
moz_fetch
"
node
"
"
bin
"
"
node
"
)
            
self
.
tgz_path
=
Path
(
self
.
output_dir
self
.
test_name
)
            
self
.
symbolicator_dir
=
Path
(
moz_fetch
"
symbolicator
-
cli
"
)
            
#
Extracting
crashreporter
symbols
            
zip_path
=
f
"
{
self
.
breakpad_symbol_dir
}
.
zip
"
            
with
zipfile
.
ZipFile
(
zip_path
"
r
"
)
as
zipf
:
                
zipf
.
extractall
(
self
.
breakpad_symbol_dir
)
        
else
:
            
self
.
samply_path
=
"
samply
"
#
Assumed
to
be
available
via
PATH
            
self
.
node_path
=
Path
(
find_node_executable
(
)
[
0
]
)
.
resolve
(
)
            
self
.
breakpad_symbol_dir
self
.
symbolicator_dir
=
(
                
self
.
_validate_symbolication_paths
(
                    
self
.
get_arg
(
"
symbol
-
path
"
None
)
                    
self
.
get_arg
(
"
symbolicator
-
path
"
None
)
                
)
            
)
    
def
_get_perf_data
(
self
)
:
        
"
"
"
Retrieve
all
the
perf
.
data
profiles
generated
by
simpleperf
.
On
CI
        
.
tgz
file
containing
the
profiles
needs
to
be
extracted
first
.
        
:
return
list
[
pathlib
.
Path
]
:
Returns
list
of
paths
to
perf
.
data
files
        
"
"
"
        
data_dir
=
self
.
output_dir
        
if
ON_TRY
:
            
#
Extract
perf
.
data
files
            
tgz_file
=
Path
(
f
"
{
self
.
tgz_path
}
.
tgz
"
)
            
with
tarfile
.
open
(
tgz_file
"
r
:
gz
"
)
as
tar
:
                
tar
.
extractall
(
path
=
self
.
work_dir
)
            
data_dir
=
self
.
work_dir
        
perf_data
=
[
            
data_file
            
for
data_file
in
Path
(
data_dir
)
.
rglob
(
"
*
.
data
"
)
            
if
data_file
.
is_file
(
)
        
]
        
return
perf_data
    
def
_convert_perf_to_json
(
self
perf_data
)
:
        
"
"
"
Convert
perf
.
data
files
into
.
json
files
into
the
Firefox
Profiler
'
s
        
processed
profile
format
.
        
:
param
perf_data
list
[
pathlib
.
Path
]
:
list
of
paths
to
perf
.
data
files
        
:
return
list
[
pathlib
.
Path
]
:
Returns
list
of
paths
to
.
json
profiles
        
"
"
"
        
unsymbolicated_profiles
=
[
]
        
#
Convert
perf
.
data
to
unsymbolicated
.
json
profiles
        
for
file_path
in
perf_data
:
            
filename
=
file_path
.
stem
            
number
=
filename
.
split
(
"
-
"
)
[
-
1
]
            
output_path
=
Path
(
self
.
work_dir
f
"
profile
-
{
number
}
-
unsymbolicated
.
json
"
)
            
#
Run
samply
import
as
a
blocking
command
to
ensure
perf
.
data
            
#
is
processed
to
profile
.
json
before
proceeding
            
with
subprocess
.
Popen
(
                
[
                    
str
(
self
.
samply_path
)
                    
"
import
"
                    
str
(
file_path
)
                    
"
-
-
save
-
only
"
                    
"
-
o
"
                    
str
(
output_path
)
                
]
                
stdout
=
subprocess
.
PIPE
                
stderr
=
subprocess
.
STDOUT
                
text
=
True
                
bufsize
=
1
            
)
as
samply_process
:
                
#
Stream
and
forward
to
self
.
info
(
)
                
for
line
in
samply_process
.
stdout
:
                    
self
.
info
(
f
"
samply
{
line
.
strip
(
)
}
"
)
            
unsymbolicated_profiles
.
append
(
output_path
)
        
unsymbolicated_profiles
.
sort
(
)
        
return
unsymbolicated_profiles
    
def
_symbolicate_profiles
(
self
unsymbolicated_profiles
)
:
        
"
"
"
Symbolicate
.
json
profiles
.
This
involves
loading
the
profiles
with
        
samply
capturing
the
symbol
server
url
and
processing
the
files
with
        
symbolicator
-
cli
.
        
:
param
unsymbolicated_profiles
list
[
pathlib
.
Path
]
:
list
of
paths
to
unsymbolicated
            
profile
.
json
files
in
processed
profile
format
.
        
:
raises
SimpleperfSymbolicationTimeoutError
:
Error
if
obtaining
the
symbol
server
URL
            
from
the
samply
process
exceeds
SYMBOL_SERVER_TIMEOUT
seconds
.
        
:
return
list
[
pathlib
.
Path
]
:
Returns
list
of
paths
to
symbolicated
profiles
            
in
processed
profile
format
.
        
"
"
"
        
symbolicated_profiles
=
[
]
        
for
file_path
in
unsymbolicated_profiles
:
            
#
Load
unsymbolicated
profile
with
samply
            
samply_process
=
subprocess
.
Popen
(
                
[
                    
str
(
self
.
samply_path
)
                    
"
load
"
                    
str
(
file_path
)
                    
"
-
-
no
-
open
"
                    
"
-
-
breakpad
-
symbol
-
dir
"
                    
str
(
self
.
breakpad_symbol_dir
)
                    
"
-
-
breakpad
-
symbol
-
server
"
                    
BREAKPAD_SYMBOL_SERVER
                
]
                
stdout
=
subprocess
.
PIPE
                
stderr
=
subprocess
.
STDOUT
                
text
=
True
            
)
            
#
Tail
output
for
timeout
seconds
to
obtain
symbol
server
url
            
server_url
=
"
"
            
start
=
time
.
time
(
)
            
with
samply_process
.
stdout
:
                
for
line
in
iter
(
samply_process
.
stdout
.
readline
b
"
"
)
:
                    
if
line
.
startswith
(
"
http
"
)
:
                        
url
=
unquote
(
line
)
                        
server_url
=
str
(
url
.
split
(
"
symbolServer
=
"
1
)
[
-
1
]
)
                        
break
                    
if
(
time
.
time
(
)
-
start
)
>
SYMBOL_SERVER_TIMEOUT
:
                        
raise
SimpleperfSymbolicationTimeoutError
(
                            
f
"
Timed
out
after
{
SYMBOL_SERVER_TIMEOUT
}
seconds
while
waiting
for
samply
server
to
start
"
                        
)
            
#
Symbolicate
profiles
with
a
blocking
symbolicator
-
cli
call
            
input_profile_path
=
file_path
            
filename
=
file_path
.
stem
.
replace
(
"
-
unsymbolicated
"
"
"
)
            
output_profile_path
=
Path
(
self
.
work_dir
f
"
{
filename
}
.
json
"
)
            
with
subprocess
.
Popen
(
                
[
                    
str
(
self
.
node_path
)
                    
str
(
Path
(
self
.
symbolicator_dir
"
symbolicator
-
cli
.
js
"
)
)
                    
"
-
-
input
"
                    
str
(
input_profile_path
)
                    
"
-
-
output
"
                    
str
(
output_profile_path
)
                    
"
-
-
server
"
                    
server_url
                
]
                
stdout
=
subprocess
.
PIPE
                
stderr
=
subprocess
.
STDOUT
                
text
=
True
                
bufsize
=
1
            
)
as
symbolicator_process
:
                
#
Stream
and
forward
to
self
.
info
(
)
                
for
line
in
symbolicator_process
.
stdout
:
                    
self
.
info
(
f
"
symbolicator
-
cli
{
line
.
strip
(
)
}
"
)
            
symbolicated_profiles
.
append
(
output_profile_path
)
            
#
Terminate
samply
server
            
samply_process
.
send_signal
(
signal
.
SIGINT
)
            
samply_process
.
wait
(
)
        
return
symbolicated_profiles
    
def
_archive_profiles
(
self
symbolicated_profiles
)
:
        
"
"
"
Archive
all
symbolicated
profiles
into
a
compressed
.
zip
file
.
        
:
param
symbolicated_profiles
list
[
pathlib
.
Path
]
:
List
of
paths
to
symbolicated
            
profile
.
json
files
to
be
archived
.
        
"
"
"
        
#
Archive
and
export
symbolicated
profiles
        
symbolicated_profiles
.
sort
(
)
        
output_zip_path
=
Path
(
self
.
output_dir
f
"
profile_
{
self
.
test_name
}
.
zip
"
)
        
with
zipfile
.
ZipFile
(
output_zip_path
"
w
"
)
as
zipf
:
            
for
file_path
in
symbolicated_profiles
:
                
zipf
.
write
(
file_path
arcname
=
file_path
.
name
)
    
def
_symbolicate
(
self
)
:
        
"
"
"
Convert
perf
data
to
symbolicated
profiles
.
        
This
method
works
for
tests
run
locally
and
in
CI
.
When
run
        
locally
it
assumes
that
samply
is
already
        
installed
on
the
system
.
Additionally
local
paths
to
        
the
directories
containing
Breakpad
symbols
and
a
build
of
        
symbolicator
-
cli
must
be
provided
via
command
-
line
arguments
for
        
local
symbolication
.
        
"
"
"
        
try
:
            
self
.
info
(
"
Preparing
symbolication
environment
"
)
            
self
.
_prepare_symbolication_environment
(
)
            
self
.
info
(
"
Obtaining
perf
.
data
files
"
)
            
perf_data
=
self
.
_get_perf_data
(
)
            
self
.
info
(
"
Converting
perf
.
data
files
to
profile
.
json
files
"
)
            
unsymbolicated_profiles
=
self
.
_convert_perf_to_json
(
perf_data
)
            
self
.
info
(
"
Symbolicating
profile
.
json
files
"
)
            
symbolicated_profiles
=
self
.
_symbolicate_profiles
(
unsymbolicated_profiles
)
            
self
.
info
(
"
Archiving
symbolicated
profile
.
json
files
"
)
            
self
.
_archive_profiles
(
symbolicated_profiles
)
        
except
SimpleperfSymbolicationError
as
e
:
            
#
If
flags
are
not
provided
/
invalid
skip
this
symbolication
step
completely
            
self
.
warning
(
                
f
"
Failed
to
prepare
symbolication
environment
.
Skipping
profile
symbolication
:
{
e
}
"
            
)
        
except
SimpleperfSymbolicationTimeoutError
as
e
:
            
self
.
warning
(
                
f
"
Timed
out
after
while
waiting
for
samply
server
.
Skipping
profile
symbolication
:
{
e
}
"
            
)
        
finally
:
            
if
self
.
work_dir
.
exists
(
)
:
                
shutil
.
rmtree
(
self
.
work_dir
)
#
Ensure
cleanup
    
def
teardown
(
self
)
:
        
self
.
_symbolicate
(
)
        
self
.
_cleanup
(
)
    
def
run
(
self
metadata
)
:
        
"
"
"
Run
the
simpleperf
layer
.
        
The
run
step
of
the
simpleperf
layer
is
a
no
-
op
since
the
expectation
is
that
        
the
start
/
stop
controls
are
manually
called
through
the
ProfilerMediator
.
        
"
"
"
        
self
.
test_name
=
metadata
.
script
[
"
name
"
]
        
metadata
.
add_extra_options
(
[
"
simpleperf
"
]
)
        
return
metadata
