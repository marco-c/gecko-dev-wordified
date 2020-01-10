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
from
__future__
import
absolute_import
print_function
unicode_literals
import
argparse
import
hashlib
import
json
import
os
import
re
import
subprocess
import
shutil
import
tempfile
import
yaml
from
mach
.
decorators
import
(
    
CommandArgument
    
CommandProvider
    
Command
    
SubCommand
)
from
mozbuild
.
base
import
(
    
MachCommandBase
    
MachCommandConditions
as
conditions
)
from
mozbuild
.
util
import
ensureParentDir
from
collections
import
OrderedDict
from
mozbuild
.
backend
import
backends
import
mozpack
.
path
as
mozpath
from
mozbuild
.
artifact_builds
import
JOB_CHOICES
from
mozversioncontrol
import
get_repository_object
import
logging
BUILD_WHAT_HELP
=
"
"
"
What
to
build
.
Can
be
a
top
-
level
make
target
or
a
relative
directory
.
If
multiple
options
are
provided
they
will
be
built
serially
.
Takes
dependency
information
from
topsrcdir
/
build
/
dumbmake
-
dependencies
to
build
additional
targets
as
needed
.
BUILDING
ONLY
PARTS
OF
THE
TREE
CAN
RESULT
IN
BAD
TREE
STATE
.
USE
AT
YOUR
OWN
RISK
.
"
"
"
.
strip
(
)
#
Function
used
to
run
clang
-
format
on
a
batch
of
files
.
It
is
a
helper
function
#
in
order
to
integrate
into
the
futures
ecosystem
clang
-
format
.
def
run_one_clang_format_batch
(
args
)
:
    
try
:
        
subprocess
.
check_output
(
args
)
    
except
subprocess
.
CalledProcessError
as
e
:
        
return
e
CommandProvider
class
Build
(
MachCommandBase
)
:
    
"
"
"
Interface
to
build
the
tree
.
"
"
"
    
Command
(
'
build
'
category
=
'
build
'
description
=
'
Build
the
tree
.
'
)
    
CommandArgument
(
'
-
-
jobs
'
'
-
j
'
default
=
'
0
'
metavar
=
'
jobs
'
type
=
int
                     
help
=
'
Number
of
concurrent
jobs
to
run
.
Default
is
the
number
of
CPUs
.
'
)
    
CommandArgument
(
'
-
C
'
'
-
-
directory
'
default
=
None
                     
help
=
'
Change
to
a
subdirectory
of
the
build
directory
first
.
'
)
    
CommandArgument
(
'
what
'
default
=
None
nargs
=
'
*
'
help
=
BUILD_WHAT_HELP
)
    
CommandArgument
(
'
-
X
'
'
-
-
disable
-
extra
-
make
-
dependencies
'
                     
default
=
False
action
=
'
store_true
'
                     
help
=
'
Do
not
add
extra
make
dependencies
.
'
)
    
CommandArgument
(
'
-
v
'
'
-
-
verbose
'
action
=
'
store_true
'
                     
help
=
'
Verbose
output
for
what
commands
the
build
is
running
.
'
)
    
CommandArgument
(
'
-
-
keep
-
going
'
action
=
'
store_true
'
                     
help
=
'
Keep
building
after
an
error
has
occurred
'
)
    
def
build
(
self
what
=
None
disable_extra_make_dependencies
=
None
jobs
=
0
              
directory
=
None
verbose
=
False
keep_going
=
False
)
:
        
"
"
"
Build
the
source
tree
.
        
With
no
arguments
this
will
perform
a
full
build
.
        
Positional
arguments
define
targets
to
build
.
These
can
be
make
targets
        
or
patterns
like
"
<
dir
>
/
<
target
>
"
to
indicate
a
make
target
within
a
        
directory
.
        
There
are
a
few
special
targets
that
can
be
used
to
perform
a
partial
        
build
faster
than
what
mach
build
would
perform
:
        
*
binaries
-
compiles
and
links
all
C
/
C
+
+
sources
and
produces
shared
          
libraries
and
executables
(
binaries
)
.
        
*
faster
-
builds
JavaScript
XUL
CSS
etc
files
.
        
"
binaries
"
and
"
faster
"
almost
fully
complement
each
other
.
However
        
there
are
build
actions
not
captured
by
either
.
If
things
don
'
t
appear
to
        
be
rebuilding
perform
a
vanilla
mach
build
to
rebuild
the
world
.
        
"
"
"
        
from
mozbuild
.
controller
.
building
import
BuildDriver
        
self
.
log_manager
.
enable_all_structured_loggers
(
)
        
driver
=
self
.
_spawn
(
BuildDriver
)
        
return
driver
.
build
(
            
what
=
what
            
disable_extra_make_dependencies
=
disable_extra_make_dependencies
            
jobs
=
jobs
            
directory
=
directory
            
verbose
=
verbose
            
keep_going
=
keep_going
            
mach_context
=
self
.
_mach_context
)
    
Command
(
'
configure
'
category
=
'
build
'
             
description
=
'
Configure
the
tree
(
run
configure
and
config
.
status
)
.
'
)
    
CommandArgument
(
'
options
'
default
=
None
nargs
=
argparse
.
REMAINDER
                     
help
=
'
Configure
options
'
)
    
def
configure
(
self
options
=
None
buildstatus_messages
=
False
line_handler
=
None
)
:
        
from
mozbuild
.
controller
.
building
import
BuildDriver
        
self
.
log_manager
.
enable_all_structured_loggers
(
)
        
driver
=
self
.
_spawn
(
BuildDriver
)
        
return
driver
.
configure
(
            
options
=
options
            
buildstatus_messages
=
buildstatus_messages
            
line_handler
=
line_handler
)
    
Command
(
'
resource
-
usage
'
category
=
'
post
-
build
'
             
description
=
'
Show
information
about
system
resource
usage
for
a
build
.
'
)
    
CommandArgument
(
'
-
-
address
'
default
=
'
localhost
'
                     
help
=
'
Address
the
HTTP
server
should
listen
on
.
'
)
    
CommandArgument
(
'
-
-
port
'
type
=
int
default
=
0
                     
help
=
'
Port
number
the
HTTP
server
should
listen
on
.
'
)
    
CommandArgument
(
'
-
-
browser
'
default
=
'
firefox
'
                     
help
=
'
Web
browser
to
automatically
open
.
See
webbrowser
Python
module
.
'
)
    
CommandArgument
(
'
-
-
url
'
                     
help
=
'
URL
of
JSON
document
to
display
'
)
    
def
resource_usage
(
self
address
=
None
port
=
None
browser
=
None
url
=
None
)
:
        
import
webbrowser
        
from
mozbuild
.
html_build_viewer
import
BuildViewerServer
        
server
=
BuildViewerServer
(
address
port
)
        
if
url
:
            
server
.
add_resource_json_url
(
"
url
"
url
)
        
else
:
            
last
=
self
.
_get_state_filename
(
"
build_resources
.
json
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
last
)
:
                
print
(
'
Build
resources
not
available
.
If
you
have
performed
a
'
                      
'
build
and
receive
this
message
the
psutil
Python
package
'
                      
'
likely
failed
to
initialize
properly
.
'
)
                
return
1
            
server
.
add_resource_json_file
(
"
last
"
last
)
        
try
:
            
webbrowser
.
get
(
browser
)
.
open_new_tab
(
server
.
url
)
        
except
Exception
:
            
print
(
"
Cannot
get
browser
specified
trying
the
default
instead
.
"
)
            
try
:
                
browser
=
webbrowser
.
get
(
)
.
open_new_tab
(
server
.
url
)
            
except
Exception
:
                
print
(
"
Please
open
%
s
in
a
browser
.
"
%
server
.
url
)
        
print
(
"
Hit
CTRL
+
c
to
stop
server
.
"
)
        
server
.
run
(
)
    
Command
(
'
build
-
backend
'
category
=
'
build
'
             
description
=
'
Generate
a
backend
used
to
build
the
tree
.
'
)
    
CommandArgument
(
'
-
d
'
'
-
-
diff
'
action
=
'
store_true
'
                     
help
=
'
Show
a
diff
of
changes
.
'
)
    
#
It
would
be
nice
to
filter
the
choices
below
based
on
    
#
conditions
but
that
is
for
another
day
.
    
CommandArgument
(
'
-
b
'
'
-
-
backend
'
nargs
=
'
+
'
choices
=
sorted
(
backends
)
                     
help
=
'
Which
backend
to
build
.
'
)
    
CommandArgument
(
'
-
v
'
'
-
-
verbose
'
action
=
'
store_true
'
                     
help
=
'
Verbose
output
.
'
)
    
CommandArgument
(
'
-
n
'
'
-
-
dry
-
run
'
action
=
'
store_true
'
                     
help
=
'
Do
everything
except
writing
files
out
.
'
)
    
def
build_backend
(
self
backend
diff
=
False
verbose
=
False
dry_run
=
False
)
:
        
python
=
self
.
virtualenv_manager
.
python_path
        
config_status
=
os
.
path
.
join
(
self
.
topobjdir
"
config
.
status
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
config_status
)
:
            
print
(
                
"
config
.
status
not
found
.
Please
run
|
mach
configure
|
"
                
"
or
|
mach
build
|
prior
to
building
the
%
s
build
backend
.
"
%
backend
            
)
            
return
1
        
args
=
[
python
config_status
]
        
if
backend
:
            
args
.
append
(
"
-
-
backend
"
)
            
args
.
extend
(
backend
)
        
if
diff
:
            
args
.
append
(
"
-
-
diff
"
)
        
if
verbose
:
            
args
.
append
(
"
-
-
verbose
"
)
        
if
dry_run
:
            
args
.
append
(
'
-
-
dry
-
run
'
)
        
return
self
.
_run_command_in_objdir
(
args
=
args
pass_thru
=
True
                                           
ensure_exit_code
=
False
)
CommandProvider
class
ClangCommands
(
MachCommandBase
)
:
    
Command
(
'
clang
-
complete
'
category
=
'
devenv
'
             
description
=
'
Generate
a
.
clang_complete
file
.
'
)
    
def
clang_complete
(
self
)
:
        
import
shlex
        
build_vars
=
{
}
        
def
on_line
(
line
)
:
            
elements
=
[
s
.
strip
(
)
for
s
in
line
.
split
(
'
=
'
1
)
]
            
if
len
(
elements
)
!
=
2
:
                
return
            
build_vars
[
elements
[
0
]
]
=
elements
[
1
]
        
try
:
            
old_logger
=
self
.
log_manager
.
replace_terminal_handler
(
None
)
            
self
.
_run_make
(
target
=
'
showbuild
'
log
=
False
line_handler
=
on_line
)
        
finally
:
            
self
.
log_manager
.
replace_terminal_handler
(
old_logger
)
        
def
print_from_variable
(
name
)
:
            
if
name
not
in
build_vars
:
                
return
            
value
=
build_vars
[
name
]
            
value
=
value
.
replace
(
'
-
I
.
'
'
-
I
%
s
'
%
self
.
topobjdir
)
            
value
=
value
.
replace
(
'
.
'
'
%
s
'
%
self
.
topobjdir
)
            
value
=
value
.
replace
(
'
-
I
.
.
'
'
-
I
%
s
/
.
.
'
%
self
.
topobjdir
)
            
value
=
value
.
replace
(
'
.
.
'
'
%
s
/
.
.
'
%
self
.
topobjdir
)
            
args
=
shlex
.
split
(
value
)
            
for
i
in
range
(
0
len
(
args
)
-
1
)
:
                
arg
=
args
[
i
]
                
if
arg
.
startswith
(
(
'
-
I
'
'
-
D
'
)
)
:
                    
print
(
arg
)
                    
continue
                
if
arg
.
startswith
(
'
-
include
'
)
:
                    
print
(
arg
+
'
'
+
args
[
i
+
1
]
)
                    
continue
        
print_from_variable
(
'
COMPILE_CXXFLAGS
'
)
        
print
(
'
-
I
%
s
/
ipc
/
chromium
/
src
'
%
self
.
topsrcdir
)
        
print
(
'
-
I
%
s
/
ipc
/
glue
'
%
self
.
topsrcdir
)
        
print
(
'
-
I
%
s
/
ipc
/
ipdl
/
_ipdlheaders
'
%
self
.
topobjdir
)
class
StaticAnalysisMonitor
(
object
)
:
    
def
__init__
(
self
srcdir
objdir
clang_tidy_config
total
)
:
        
self
.
_total
=
total
        
self
.
_processed
=
0
        
self
.
_current
=
None
        
self
.
_srcdir
=
srcdir
        
self
.
_clang_tidy_config
=
clang_tidy_config
[
"
clang_checkers
"
]
        
#
Transform
the
configuration
to
support
Regex
        
for
item
in
self
.
_clang_tidy_config
:
            
if
item
[
"
name
"
]
=
=
"
-
*
"
:
                
continue
            
item
[
"
name
"
]
.
replace
(
"
*
"
"
.
*
"
)
        
from
mozbuild
.
compilation
.
warnings
import
WarningsCollector
WarningsDatabase
        
self
.
_warnings_database
=
WarningsDatabase
(
)
        
def
on_warning
(
warning
)
:
            
self
.
_warnings_database
.
insert
(
warning
)
        
self
.
_warnings_collector
=
WarningsCollector
(
on_warning
objdir
=
objdir
)
    
property
    
def
num_files
(
self
)
:
        
return
self
.
_total
    
property
    
def
num_files_processed
(
self
)
:
        
return
self
.
_processed
    
property
    
def
current_file
(
self
)
:
        
return
self
.
_current
    
property
    
def
warnings_db
(
self
)
:
        
return
self
.
_warnings_database
    
def
on_line
(
self
line
)
:
        
warning
=
None
        
try
:
            
warning
=
self
.
_warnings_collector
.
process_line
(
line
)
        
except
Exception
:
            
pass
        
if
line
.
find
(
"
clang
-
tidy
"
)
!
=
-
1
:
            
filename
=
line
.
split
(
"
"
)
[
-
1
]
            
if
os
.
path
.
isfile
(
filename
)
:
                
self
.
_current
=
os
.
path
.
relpath
(
filename
self
.
_srcdir
)
            
else
:
                
self
.
_current
=
None
            
self
.
_processed
=
self
.
_processed
+
1
            
return
(
warning
False
)
        
if
warning
is
not
None
:
            
def
get_reliability
(
checker_name
)
:
                
#
get
the
matcher
from
self
.
_clang_tidy_config
that
is
the
'
name
'
field
                
reliability
=
None
                
for
item
in
self
.
_clang_tidy_config
:
                    
if
item
[
"
name
"
]
=
=
checker_name
:
                        
reliability
=
item
.
get
(
"
reliability
"
"
low
"
)
                        
break
                    
else
:
                        
#
We
are
using
a
regex
in
order
to
also
match
'
mozilla
-
.
*
like
checkers
'
                        
matcher
=
re
.
match
(
item
[
"
name
"
]
checker_name
)
                        
if
matcher
is
not
None
and
matcher
.
group
(
0
)
=
=
checker_name
:
                            
reliability
=
item
.
get
(
"
reliability
"
"
low
"
)
                            
break
                
return
reliability
            
reliability
=
get_reliability
(
warning
[
"
flag
"
]
)
            
if
reliability
is
not
None
:
                
warning
[
"
reliability
"
]
=
reliability
        
return
(
warning
True
)
class
ArtifactSubCommand
(
SubCommand
)
:
    
def
__call__
(
self
func
)
:
        
after
=
SubCommand
.
__call__
(
self
func
)
        
args
=
[
            
CommandArgument
(
'
-
-
tree
'
metavar
=
'
TREE
'
type
=
str
                            
help
=
'
Firefox
tree
.
'
)
            
CommandArgument
(
'
-
-
job
'
metavar
=
'
JOB
'
choices
=
JOB_CHOICES
                            
help
=
'
Build
job
.
'
)
            
CommandArgument
(
'
-
-
verbose
'
'
-
v
'
action
=
'
store_true
'
                            
help
=
'
Print
verbose
output
.
'
)
        
]
        
for
arg
in
args
:
            
after
=
arg
(
after
)
        
return
after
class
SymbolsAction
(
argparse
.
Action
)
:
    
def
__call__
(
self
parser
namespace
values
option_string
=
None
)
:
        
#
If
this
function
is
called
it
means
the
-
-
symbols
option
was
given
        
#
so
we
want
to
store
the
value
True
if
no
explicit
value
was
given
        
#
to
the
option
.
        
setattr
(
namespace
self
.
dest
values
or
True
)
CommandProvider
class
PackageFrontend
(
MachCommandBase
)
:
    
"
"
"
Fetch
and
install
binary
artifacts
from
Mozilla
automation
.
"
"
"
    
Command
(
'
artifact
'
category
=
'
post
-
build
'
             
description
=
'
Use
pre
-
built
artifacts
to
build
Firefox
.
'
)
    
def
artifact
(
self
)
:
        
'
'
'
Download
cache
and
install
pre
-
built
binary
artifacts
to
build
Firefox
.
        
Use
|
mach
build
|
as
normal
to
freshen
your
installed
binary
libraries
:
        
artifact
builds
automatically
download
cache
and
install
binary
        
artifacts
from
Mozilla
automation
replacing
whatever
may
be
in
your
        
object
directory
.
Use
|
mach
artifact
last
|
to
see
what
binary
artifacts
        
were
last
used
.
        
Never
build
libxul
again
!
        
'
'
'
        
pass
    
def
_make_artifacts
(
self
tree
=
None
job
=
None
skip_cache
=
False
                        
download_tests
=
True
download_symbols
=
False
                        
download_host_bins
=
False
                        
download_maven_zip
=
False
                        
no_process
=
False
)
:
        
state_dir
=
self
.
_mach_context
.
state_dir
        
cache_dir
=
os
.
path
.
join
(
state_dir
'
package
-
frontend
'
)
        
hg
=
None
        
if
conditions
.
is_hg
(
self
)
:
            
hg
=
self
.
substs
[
'
HG
'
]
        
git
=
None
        
if
conditions
.
is_git
(
self
)
:
            
git
=
self
.
substs
[
'
GIT
'
]
        
#
If
we
'
re
building
Thunderbird
we
should
be
checking
for
comm
-
central
artifacts
.
        
topsrcdir
=
self
.
substs
.
get
(
'
commtopsrcdir
'
self
.
topsrcdir
)
        
if
download_maven_zip
:
            
if
download_tests
:
                
raise
ValueError
(
'
-
-
maven
-
zip
requires
-
-
no
-
tests
'
)
            
if
download_symbols
:
                
raise
ValueError
(
'
-
-
maven
-
zip
requires
no
-
-
symbols
'
)
            
if
download_host_bins
:
                
raise
ValueError
(
'
-
-
maven
-
zip
requires
no
-
-
host
-
bins
'
)
            
if
not
no_process
:
                
raise
ValueError
(
'
-
-
maven
-
zip
requires
-
-
no
-
process
'
)
        
from
mozbuild
.
artifacts
import
Artifacts
        
artifacts
=
Artifacts
(
tree
self
.
substs
self
.
defines
job
                              
log
=
self
.
log
cache_dir
=
cache_dir
                              
skip_cache
=
skip_cache
hg
=
hg
git
=
git
                              
topsrcdir
=
topsrcdir
                              
download_tests
=
download_tests
                              
download_symbols
=
download_symbols
                              
download_host_bins
=
download_host_bins
                              
download_maven_zip
=
download_maven_zip
                              
no_process
=
no_process
)
        
return
artifacts
    
ArtifactSubCommand
(
'
artifact
'
'
install
'
                        
'
Install
a
good
pre
-
built
artifact
.
'
)
    
CommandArgument
(
'
source
'
metavar
=
'
SRC
'
nargs
=
'
?
'
type
=
str
                     
help
=
'
Where
to
fetch
and
install
artifacts
from
.
Can
be
omitted
in
'
                     
'
which
case
the
current
hg
repository
is
inspected
;
an
hg
revision
;
'
                     
'
a
remote
URL
;
or
a
local
file
.
'
                     
default
=
None
)
    
CommandArgument
(
'
-
-
skip
-
cache
'
action
=
'
store_true
'
                     
help
=
'
Skip
all
local
caches
to
force
re
-
fetching
remote
artifacts
.
'
                     
default
=
False
)
    
CommandArgument
(
'
-
-
no
-
tests
'
action
=
'
store_true
'
help
=
"
Don
'
t
install
tests
.
"
)
    
CommandArgument
(
'
-
-
symbols
'
nargs
=
'
?
'
action
=
SymbolsAction
help
=
'
Download
symbols
.
'
)
    
CommandArgument
(
'
-
-
host
-
bins
'
action
=
'
store_true
'
help
=
'
Download
host
binaries
.
'
)
    
CommandArgument
(
'
-
-
distdir
'
help
=
'
Where
to
install
artifacts
to
.
'
)
    
CommandArgument
(
'
-
-
no
-
process
'
action
=
'
store_true
'
                     
help
=
"
Don
'
t
process
(
unpack
)
artifact
packages
just
download
them
.
"
)
    
CommandArgument
(
'
-
-
maven
-
zip
'
action
=
'
store_true
'
help
=
"
Download
Maven
zip
(
Android
-
only
)
.
"
)
    
def
artifact_install
(
self
source
=
None
skip_cache
=
False
tree
=
None
job
=
None
verbose
=
False
                         
no_tests
=
False
symbols
=
False
host_bins
=
False
distdir
=
None
                         
no_process
=
False
maven_zip
=
False
)
:
        
self
.
_set_log_level
(
verbose
)
        
artifacts
=
self
.
_make_artifacts
(
tree
=
tree
job
=
job
skip_cache
=
skip_cache
                                         
download_tests
=
not
no_tests
                                         
download_symbols
=
symbols
                                         
download_host_bins
=
host_bins
                                         
download_maven_zip
=
maven_zip
                                         
no_process
=
no_process
)
        
return
artifacts
.
install_from
(
source
distdir
or
self
.
distdir
)
    
ArtifactSubCommand
(
'
artifact
'
'
clear
-
cache
'
                        
'
Delete
local
artifacts
and
reset
local
artifact
cache
.
'
)
    
def
artifact_clear_cache
(
self
tree
=
None
job
=
None
verbose
=
False
)
:
        
self
.
_set_log_level
(
verbose
)
        
artifacts
=
self
.
_make_artifacts
(
tree
=
tree
job
=
job
)
        
artifacts
.
clear_cache
(
)
        
return
0
    
SubCommand
(
'
artifact
'
'
toolchain
'
)
    
CommandArgument
(
'
-
-
verbose
'
'
-
v
'
action
=
'
store_true
'
                     
help
=
'
Print
verbose
output
.
'
)
    
CommandArgument
(
'
-
-
cache
-
dir
'
metavar
=
'
DIR
'
                     
help
=
'
Directory
where
to
store
the
artifacts
cache
'
)
    
CommandArgument
(
'
-
-
skip
-
cache
'
action
=
'
store_true
'
                     
help
=
'
Skip
all
local
caches
to
force
re
-
fetching
remote
artifacts
.
'
                     
default
=
False
)
    
CommandArgument
(
'
-
-
from
-
build
'
metavar
=
'
BUILD
'
nargs
=
'
+
'
                     
help
=
'
Download
toolchains
resulting
from
the
given
build
(
s
)
;
'
                     
'
BUILD
is
a
name
of
a
toolchain
task
e
.
g
.
linux64
-
clang
'
)
    
CommandArgument
(
'
-
-
tooltool
-
manifest
'
metavar
=
'
MANIFEST
'
                     
help
=
'
Explicit
tooltool
manifest
to
process
'
)
    
CommandArgument
(
'
-
-
authentication
-
file
'
metavar
=
'
FILE
'
                     
help
=
'
Use
the
RelengAPI
token
found
in
the
given
file
to
authenticate
'
)
    
CommandArgument
(
'
-
-
tooltool
-
url
'
metavar
=
'
URL
'
                     
help
=
'
Use
the
given
url
as
tooltool
server
'
)
    
CommandArgument
(
'
-
-
no
-
unpack
'
action
=
'
store_true
'
                     
help
=
'
Do
not
unpack
any
downloaded
file
'
)
    
CommandArgument
(
'
-
-
retry
'
type
=
int
default
=
4
                     
help
=
'
Number
of
times
to
retry
failed
downloads
'
)
    
CommandArgument
(
'
-
-
artifact
-
manifest
'
metavar
=
'
FILE
'
                     
help
=
'
Store
a
manifest
about
the
downloaded
taskcluster
artifacts
'
)
    
CommandArgument
(
'
files
'
nargs
=
'
*
'
                     
help
=
'
A
list
of
files
to
download
in
the
form
path
task
-
id
in
'
                     
'
addition
to
the
files
listed
in
the
tooltool
manifest
.
'
)
    
def
artifact_toolchain
(
self
verbose
=
False
cache_dir
=
None
                           
skip_cache
=
False
from_build
=
(
)
                           
tooltool_manifest
=
None
authentication_file
=
None
                           
tooltool_url
=
None
no_unpack
=
False
retry
=
None
                           
artifact_manifest
=
None
files
=
(
)
)
:
        
'
'
'
Download
cache
and
install
pre
-
built
toolchains
.
        
'
'
'
        
from
mozbuild
.
artifacts
import
ArtifactCache
        
from
mozbuild
.
action
.
tooltool
import
(
            
FileRecord
            
open_manifest
            
unpack_file
        
)
        
from
requests
.
adapters
import
HTTPAdapter
        
import
redo
        
import
requests
        
from
taskgraph
.
util
.
taskcluster
import
(
            
get_artifact_url
        
)
        
self
.
_set_log_level
(
verbose
)
        
#
Normally
we
'
d
use
self
.
log_manager
.
enable_unstructured
(
)
        
#
but
that
enables
all
logging
while
we
only
really
want
tooltool
'
s
        
#
and
it
also
makes
structured
log
output
twice
.
        
#
So
we
manually
do
what
it
does
and
limit
that
to
the
tooltool
        
#
logger
.
        
if
self
.
log_manager
.
terminal_handler
:
            
logging
.
getLogger
(
'
mozbuild
.
action
.
tooltool
'
)
.
addHandler
(
                
self
.
log_manager
.
terminal_handler
)
            
logging
.
getLogger
(
'
redo
'
)
.
addHandler
(
                
self
.
log_manager
.
terminal_handler
)
            
self
.
log_manager
.
terminal_handler
.
addFilter
(
                
self
.
log_manager
.
structured_filter
)
        
if
not
cache_dir
:
            
cache_dir
=
os
.
path
.
join
(
self
.
_mach_context
.
state_dir
'
toolchains
'
)
        
tooltool_url
=
(
tooltool_url
or
                        
'
https
:
/
/
tooltool
.
mozilla
-
releng
.
net
'
)
.
rstrip
(
'
/
'
)
        
cache
=
ArtifactCache
(
cache_dir
=
cache_dir
log
=
self
.
log
                              
skip_cache
=
skip_cache
)
        
if
authentication_file
:
            
with
open
(
authentication_file
'
rb
'
)
as
f
:
                
token
=
f
.
read
(
)
.
strip
(
)
            
class
TooltoolAuthenticator
(
HTTPAdapter
)
:
                
def
send
(
self
request
*
args
*
*
kwargs
)
:
                    
request
.
headers
[
'
Authorization
'
]
=
\
                        
'
Bearer
{
}
'
.
format
(
token
)
                    
return
super
(
TooltoolAuthenticator
self
)
.
send
(
                        
request
*
args
*
*
kwargs
)
            
cache
.
_download_manager
.
session
.
mount
(
                
tooltool_url
TooltoolAuthenticator
(
)
)
        
class
DownloadRecord
(
FileRecord
)
:
            
def
__init__
(
self
url
*
args
*
*
kwargs
)
:
                
super
(
DownloadRecord
self
)
.
__init__
(
*
args
*
*
kwargs
)
                
self
.
url
=
url
                
self
.
basename
=
self
.
filename
            
def
fetch_with
(
self
cache
)
:
                
self
.
filename
=
cache
.
fetch
(
self
.
url
)
                
return
self
.
filename
            
def
validate
(
self
)
:
                
if
self
.
size
is
None
and
self
.
digest
is
None
:
                    
return
True
                
return
super
(
DownloadRecord
self
)
.
validate
(
)
        
class
ArtifactRecord
(
DownloadRecord
)
:
            
def
__init__
(
self
task_id
artifact_name
)
:
                
for
_
in
redo
.
retrier
(
attempts
=
retry
+
1
sleeptime
=
60
)
:
                    
cot
=
cache
.
_download_manager
.
session
.
get
(
                        
get_artifact_url
(
task_id
'
public
/
chain
-
of
-
trust
.
json
'
)
)
                    
if
cot
.
status_code
>
=
500
:
                        
continue
                    
cot
.
raise_for_status
(
)
                    
break
                
else
:
                    
cot
.
raise_for_status
(
)
                
digest
=
algorithm
=
None
                
data
=
json
.
loads
(
cot
.
content
)
                
for
algorithm
digest
in
(
data
.
get
(
'
artifacts
'
{
}
)
                                              
.
get
(
artifact_name
{
}
)
.
items
(
)
)
:
                    
pass
                
name
=
os
.
path
.
basename
(
artifact_name
)
                
artifact_url
=
get_artifact_url
(
task_id
artifact_name
                                                
use_proxy
=
not
artifact_name
.
startswith
(
'
public
/
'
)
)
                
super
(
ArtifactRecord
self
)
.
__init__
(
                    
artifact_url
name
                    
None
digest
algorithm
unpack
=
True
)
        
records
=
OrderedDict
(
)
        
downloaded
=
[
]
        
if
tooltool_manifest
:
            
manifest
=
open_manifest
(
tooltool_manifest
)
            
for
record
in
manifest
.
file_records
:
                
url
=
'
{
}
/
{
}
/
{
}
'
.
format
(
tooltool_url
record
.
algorithm
                                        
record
.
digest
)
                
records
[
record
.
filename
]
=
DownloadRecord
(
                    
url
record
.
filename
record
.
size
record
.
digest
                    
record
.
algorithm
unpack
=
record
.
unpack
                    
version
=
record
.
version
visibility
=
record
.
visibility
)
        
if
from_build
:
            
if
'
MOZ_AUTOMATION
'
in
os
.
environ
:
                
self
.
log
(
logging
.
ERROR
'
artifact
'
{
}
                         
'
Do
not
use
-
-
from
-
build
in
automation
;
all
dependencies
'
                         
'
should
be
determined
in
the
decision
task
.
'
)
                
return
1
            
from
taskgraph
.
optimize
import
IndexSearch
            
from
taskgraph
.
parameters
import
Parameters
            
from
taskgraph
.
generator
import
load_tasks_for_kind
            
params
=
Parameters
(
                
level
=
os
.
environ
.
get
(
'
MOZ_SCM_LEVEL
'
'
3
'
)
                
strict
=
False
            
)
            
root_dir
=
mozpath
.
join
(
self
.
topsrcdir
'
taskcluster
/
ci
'
)
            
toolchains
=
load_tasks_for_kind
(
params
'
toolchain
'
root_dir
=
root_dir
)
            
aliases
=
{
}
            
for
t
in
toolchains
.
values
(
)
:
                
alias
=
t
.
attributes
.
get
(
'
toolchain
-
alias
'
)
                
if
alias
:
                    
aliases
[
'
toolchain
-
{
}
'
.
format
(
alias
)
]
=
\
                        
t
.
task
[
'
metadata
'
]
[
'
name
'
]
            
for
b
in
from_build
:
                
user_value
=
b
                
if
not
b
.
startswith
(
'
toolchain
-
'
)
:
                    
b
=
'
toolchain
-
{
}
'
.
format
(
b
)
                
task
=
toolchains
.
get
(
aliases
.
get
(
b
b
)
)
                
if
not
task
:
                    
self
.
log
(
logging
.
ERROR
'
artifact
'
{
'
build
'
:
user_value
}
                             
'
Could
not
find
a
toolchain
build
named
{
build
}
'
)
                    
return
1
                
task_id
=
IndexSearch
(
)
.
should_replace_task
(
                    
task
{
}
task
.
optimization
.
get
(
'
index
-
search
'
[
]
)
)
                
artifact_name
=
task
.
attributes
.
get
(
'
toolchain
-
artifact
'
)
                
if
task_id
in
(
True
False
)
or
not
artifact_name
:
                    
self
.
log
(
logging
.
ERROR
'
artifact
'
{
'
build
'
:
user_value
}
                             
'
Could
not
find
artifacts
for
a
toolchain
build
'
                             
'
named
{
build
}
.
Local
commits
and
other
changes
'
                             
'
in
your
checkout
may
cause
this
error
.
Try
'
                             
'
updating
to
a
fresh
checkout
of
mozilla
-
central
'
                             
'
to
use
artifact
builds
.
'
)
                    
return
1
                
record
=
ArtifactRecord
(
task_id
artifact_name
)
                
records
[
record
.
filename
]
=
record
        
#
Handle
the
list
of
files
of
the
form
path
task
-
id
on
the
command
        
#
line
.
Each
of
those
give
a
path
to
an
artifact
to
download
.
        
for
f
in
files
:
            
if
'
'
not
in
f
:
                
self
.
log
(
logging
.
ERROR
'
artifact
'
{
}
                         
'
Expected
a
list
of
files
of
the
form
path
task
-
id
'
)
                
return
1
            
name
task_id
=
f
.
rsplit
(
'
'
1
)
            
record
=
ArtifactRecord
(
task_id
name
)
            
records
[
record
.
filename
]
=
record
        
for
record
in
records
.
itervalues
(
)
:
            
self
.
log
(
logging
.
INFO
'
artifact
'
{
'
name
'
:
record
.
basename
}
                     
'
Downloading
{
name
}
'
)
            
valid
=
False
            
#
sleeptime
is
60
per
retry
.
py
used
by
tooltool_wrapper
.
sh
            
for
attempt
_
in
enumerate
(
redo
.
retrier
(
attempts
=
retry
+
1
                                                     
sleeptime
=
60
)
)
:
                
try
:
                    
record
.
fetch_with
(
cache
)
                
except
(
requests
.
exceptions
.
HTTPError
                        
requests
.
exceptions
.
ChunkedEncodingError
                        
requests
.
exceptions
.
ConnectionError
)
as
e
:
                    
if
isinstance
(
e
requests
.
exceptions
.
HTTPError
)
:
                        
#
The
relengapi
proxy
likes
to
return
error
400
bad
request
                        
#
which
seems
improbably
to
be
due
to
our
(
simple
)
GET
                        
#
being
borked
.
                        
status
=
e
.
response
.
status_code
                        
should_retry
=
status
>
=
500
or
status
=
=
400
                    
else
:
                        
should_retry
=
True
                    
if
should_retry
or
attempt
<
retry
:
                        
level
=
logging
.
WARN
                    
else
:
                        
level
=
logging
.
ERROR
                    
#
e
.
message
is
not
always
a
string
so
convert
it
first
.
                    
self
.
log
(
level
'
artifact
'
{
}
str
(
e
.
message
)
)
                    
if
not
should_retry
:
                        
break
                    
if
attempt
<
retry
:
                        
self
.
log
(
logging
.
INFO
'
artifact
'
{
}
                                 
'
Will
retry
in
a
moment
.
.
.
'
)
                    
continue
                
try
:
                    
valid
=
record
.
validate
(
)
                
except
Exception
:
                    
pass
                
if
not
valid
:
                    
os
.
unlink
(
record
.
filename
)
                    
if
attempt
<
retry
:
                        
self
.
log
(
logging
.
INFO
'
artifact
'
{
}
                                 
'
Corrupt
download
.
Will
retry
in
a
moment
.
.
.
'
)
                    
continue
                
downloaded
.
append
(
record
)
                
break
            
if
not
valid
:
                
self
.
log
(
logging
.
ERROR
'
artifact
'
{
'
name
'
:
record
.
basename
}
                         
'
Failed
to
download
{
name
}
'
)
                
return
1
        
artifacts
=
{
}
if
artifact_manifest
else
None
        
for
record
in
downloaded
:
            
local
=
os
.
path
.
join
(
os
.
getcwd
(
)
record
.
basename
)
            
if
os
.
path
.
exists
(
local
)
:
                
os
.
unlink
(
local
)
            
#
unpack_file
needs
the
file
with
its
final
name
to
work
            
#
(
https
:
/
/
github
.
com
/
mozilla
/
build
-
tooltool
/
issues
/
38
)
so
we
            
#
need
to
copy
it
even
though
we
remove
it
later
.
Use
hard
links
            
#
when
possible
.
            
try
:
                
os
.
link
(
record
.
filename
local
)
            
except
Exception
:
                
shutil
.
copy
(
record
.
filename
local
)
            
#
Keep
a
sha256
of
each
downloaded
file
for
the
chain
-
of
-
trust
            
#
validation
.
            
if
artifact_manifest
is
not
None
:
                
with
open
(
local
)
as
fh
:
                    
h
=
hashlib
.
sha256
(
)
                    
while
True
:
                        
data
=
fh
.
read
(
1024
*
1024
)
                        
if
not
data
:
                            
break
                        
h
.
update
(
data
)
                
artifacts
[
record
.
url
]
=
{
                    
'
sha256
'
:
h
.
hexdigest
(
)
                
}
            
if
record
.
unpack
and
not
no_unpack
:
                
unpack_file
(
local
)
                
os
.
unlink
(
local
)
        
if
not
downloaded
:
            
self
.
log
(
logging
.
ERROR
'
artifact
'
{
}
'
Nothing
to
download
'
)
            
if
files
:
                
return
1
        
if
artifacts
:
            
ensureParentDir
(
artifact_manifest
)
            
with
open
(
artifact_manifest
'
w
'
)
as
fh
:
                
json
.
dump
(
artifacts
fh
indent
=
4
sort_keys
=
True
)
        
return
0
class
StaticAnalysisSubCommand
(
SubCommand
)
:
    
def
__call__
(
self
func
)
:
        
after
=
SubCommand
.
__call__
(
self
func
)
        
args
=
[
            
CommandArgument
(
'
-
-
verbose
'
'
-
v
'
action
=
'
store_true
'
                            
help
=
'
Print
verbose
output
.
'
)
        
]
        
for
arg
in
args
:
            
after
=
arg
(
after
)
        
return
after
class
StaticAnalysisMonitor
(
object
)
:
    
def
__init__
(
self
srcdir
objdir
clang_tidy_config
total
)
:
        
self
.
_total
=
total
        
self
.
_processed
=
0
        
self
.
_current
=
None
        
self
.
_srcdir
=
srcdir
        
self
.
_clang_tidy_config
=
clang_tidy_config
[
'
clang_checkers
'
]
        
#
Transform
the
configuration
to
support
Regex
        
for
item
in
self
.
_clang_tidy_config
:
            
if
item
[
'
name
'
]
=
=
'
-
*
'
:
                
continue
            
item
[
'
name
'
]
.
replace
(
'
*
'
'
.
*
'
)
        
from
mozbuild
.
compilation
.
warnings
import
(
            
WarningsCollector
            
WarningsDatabase
        
)
        
self
.
_warnings_database
=
WarningsDatabase
(
)
        
def
on_warning
(
warning
)
:
            
self
.
_warnings_database
.
insert
(
warning
)
        
self
.
_warnings_collector
=
WarningsCollector
(
on_warning
objdir
=
objdir
)
    
property
    
def
num_files
(
self
)
:
        
return
self
.
_total
    
property
    
def
num_files_processed
(
self
)
:
        
return
self
.
_processed
    
property
    
def
current_file
(
self
)
:
        
return
self
.
_current
    
property
    
def
warnings_db
(
self
)
:
        
return
self
.
_warnings_database
    
def
on_line
(
self
line
)
:
        
warning
=
None
        
try
:
            
warning
=
self
.
_warnings_collector
.
process_line
(
line
)
        
except
Exception
:
            
pass
        
if
line
.
find
(
'
clang
-
tidy
'
)
!
=
-
1
:
            
filename
=
line
.
split
(
'
'
)
[
-
1
]
            
if
os
.
path
.
isfile
(
filename
)
:
                
self
.
_current
=
os
.
path
.
relpath
(
filename
self
.
_srcdir
)
            
else
:
                
self
.
_current
=
None
            
self
.
_processed
=
self
.
_processed
+
1
            
return
(
warning
False
)
        
if
warning
is
not
None
:
            
def
get_reliability
(
checker_name
)
:
                
#
get
the
matcher
from
self
.
_clang_tidy_config
that
is
the
'
name
'
field
                
reliability
=
None
                
for
item
in
self
.
_clang_tidy_config
:
                    
if
item
[
'
name
'
]
=
=
checker_name
:
                        
reliability
=
item
.
get
(
'
reliability
'
'
low
'
)
                        
break
                    
else
:
                        
#
We
are
using
a
regex
in
order
to
also
match
'
mozilla
-
.
*
like
checkers
'
                        
matcher
=
re
.
match
(
item
[
'
name
'
]
checker_name
)
                        
if
matcher
is
not
None
and
matcher
.
group
(
0
)
=
=
checker_name
:
                            
reliability
=
item
.
get
(
'
reliability
'
'
low
'
)
                            
break
                
return
reliability
            
reliability
=
get_reliability
(
warning
[
'
flag
'
]
)
            
if
reliability
is
not
None
:
                
warning
[
'
reliability
'
]
=
reliability
        
return
(
warning
True
)
CommandProvider
class
StaticAnalysis
(
MachCommandBase
)
:
    
"
"
"
Utilities
for
running
C
+
+
static
analysis
checks
and
format
.
"
"
"
    
#
List
of
file
extension
to
consider
(
should
start
with
dot
)
    
_format_include_extensions
=
(
'
.
cpp
'
'
.
c
'
'
.
cc
'
'
.
h
'
'
.
m
'
'
.
mm
'
)
    
#
File
contaning
all
paths
to
exclude
from
formatting
    
_format_ignore_file
=
'
.
clang
-
format
-
ignore
'
    
_clang_tidy_config
=
None
    
_cov_config
=
None
    
Command
(
'
static
-
analysis
'
category
=
'
testing
'
             
description
=
'
Run
C
+
+
static
analysis
checks
'
)
    
def
static_analysis
(
self
)
:
        
#
If
not
arguments
are
provided
just
print
a
help
message
.
        
mach
=
Mach
(
os
.
getcwd
(
)
)
        
mach
.
run
(
[
'
static
-
analysis
'
'
-
-
help
'
]
)
    
StaticAnalysisSubCommand
(
'
static
-
analysis
'
'
check
'
                              
'
Run
the
checks
using
the
helper
tool
'
)
    
CommandArgument
(
'
source
'
nargs
=
'
*
'
default
=
[
'
.
*
'
]
                     
help
=
'
Source
files
to
be
analyzed
(
regex
on
path
)
.
'
                          
'
Can
be
omitted
in
which
case
the
entire
code
base
'
                          
'
is
analyzed
.
The
source
argument
is
ignored
if
'
                          
'
there
is
anything
fed
through
stdin
in
which
case
'
                          
'
the
analysis
is
only
performed
on
the
files
changed
'
                          
'
in
the
patch
streamed
through
stdin
.
This
is
called
'
                          
'
the
diff
mode
.
'
)
    
CommandArgument
(
'
-
-
checks
'
'
-
c
'
default
=
'
-
*
'
metavar
=
'
checks
'
                     
help
=
'
Static
analysis
checks
to
enable
.
By
default
this
enables
only
'
                     
'
checks
that
are
published
here
:
https
:
/
/
mzl
.
la
/
2DRHeTh
but
can
be
any
'
                     
'
clang
-
tidy
checks
syntax
.
'
)
    
CommandArgument
(
'
-
-
jobs
'
'
-
j
'
default
=
'
0
'
metavar
=
'
jobs
'
type
=
int
                     
help
=
'
Number
of
concurrent
jobs
to
run
.
Default
is
the
number
of
CPUs
.
'
)
    
CommandArgument
(
'
-
-
strip
'
'
-
p
'
default
=
'
1
'
metavar
=
'
NUM
'
                     
help
=
'
Strip
NUM
leading
components
from
file
names
in
diff
mode
.
'
)
    
CommandArgument
(
'
-
-
fix
'
'
-
f
'
default
=
False
action
=
'
store_true
'
                     
help
=
'
Try
to
autofix
errors
detected
by
clang
-
tidy
checkers
.
'
)
    
CommandArgument
(
'
-
-
header
-
filter
'
'
-
h
-
f
'
default
=
'
'
metavar
=
'
header_filter
'
                     
help
=
'
Regular
expression
matching
the
names
of
the
headers
to
'
                          
'
output
diagnostics
from
.
Diagnostics
from
the
main
file
'
                          
'
of
each
translation
unit
are
always
displayed
'
)
    
CommandArgument
(
'
-
-
output
'
'
-
o
'
default
=
None
                     
help
=
'
Write
clang
-
tidy
output
in
a
file
'
)
    
CommandArgument
(
'
-
-
format
'
default
=
'
text
'
choices
=
(
'
text
'
'
json
'
)
                     
help
=
'
Output
format
to
write
in
a
file
'
)
    
CommandArgument
(
'
-
-
outgoing
'
default
=
False
action
=
'
store_true
'
                     
help
=
'
Run
static
analysis
checks
on
outgoing
files
from
mercurial
repository
'
)
    
def
check
(
self
source
=
None
jobs
=
2
strip
=
1
verbose
=
False
checks
=
'
-
*
'
              
fix
=
False
header_filter
=
'
'
output
=
None
format
=
'
text
'
outgoing
=
False
)
:
        
from
mozbuild
.
controller
.
building
import
(
            
StaticAnalysisFooter
            
StaticAnalysisOutputManager
        
)
        
self
.
_set_log_level
(
verbose
)
        
self
.
log_manager
.
enable_all_structured_loggers
(
)
        
rc
=
self
.
_get_clang_tools
(
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
return
rc
        
if
self
.
_is_version_eligible
(
)
is
False
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
"
You
'
re
using
an
old
version
of
clang
-
format
binary
.
"
                     
"
Please
update
to
a
more
recent
one
by
running
:
'
.
/
mach
bootstrap
'
"
)
            
return
1
        
rc
=
self
.
_build_compile_db
(
verbose
=
verbose
)
        
rc
=
rc
or
self
.
_build_export
(
jobs
=
jobs
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
return
rc
        
#
Use
outgoing
files
instead
of
source
files
        
if
outgoing
:
            
repo
=
get_repository_object
(
self
.
topsrcdir
)
            
files
=
repo
.
get_outgoing_files
(
)
            
source
=
map
(
os
.
path
.
abspath
files
)
        
#
Split
in
several
chunks
to
avoid
hitting
Python
'
s
limit
of
100
groups
in
re
        
compile_db
=
json
.
loads
(
open
(
self
.
_compile_db
'
r
'
)
.
read
(
)
)
        
total
=
0
        
import
re
        
chunk_size
=
50
        
for
offset
in
range
(
0
len
(
source
)
chunk_size
)
:
            
source_chunks
=
source
[
offset
:
offset
+
chunk_size
]
            
name_re
=
re
.
compile
(
'
(
'
+
'
)
|
(
'
.
join
(
source_chunks
)
+
'
)
'
)
            
for
f
in
compile_db
:
                
if
name_re
.
search
(
f
[
'
file
'
]
)
:
                    
total
=
total
+
1
        
if
not
total
:
            
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                     
"
There
are
no
files
eligible
for
analysis
.
Please
note
that
'
header
'
files
"
                     
"
cannot
be
used
for
analysis
since
they
do
not
consist
compilation
units
.
"
)
            
return
0
        
cwd
=
self
.
topobjdir
        
self
.
_compilation_commands_path
=
self
.
topobjdir
        
if
self
.
_clang_tidy_config
is
None
:
            
self
.
_clang_tidy_config
=
self
.
_get_clang_tidy_config
(
)
        
args
=
self
.
_get_clang_tidy_command
(
            
checks
=
checks
header_filter
=
header_filter
sources
=
source
jobs
=
jobs
fix
=
fix
)
        
monitor
=
StaticAnalysisMonitor
(
            
self
.
topsrcdir
self
.
topobjdir
self
.
_clang_tidy_config
total
)
        
footer
=
StaticAnalysisFooter
(
self
.
log_manager
.
terminal
monitor
)
        
with
StaticAnalysisOutputManager
(
self
.
log_manager
monitor
footer
)
as
output_manager
:
            
rc
=
self
.
run_process
(
args
=
args
ensure_exit_code
=
False
                                  
line_handler
=
output_manager
.
on_line
cwd
=
cwd
)
            
self
.
log
(
logging
.
WARNING
'
warning_summary
'
                     
{
'
count
'
:
len
(
monitor
.
warnings_db
)
}
                     
'
{
count
}
warnings
present
.
'
)
            
#
Write
output
file
            
if
output
is
not
None
:
                
output_manager
.
write
(
output
format
)
        
if
rc
!
=
0
:
            
return
rc
        
#
if
we
are
building
firefox
for
android
it
might
be
nice
to
        
#
also
analyze
the
java
code
base
        
if
self
.
substs
[
'
MOZ_BUILD_APP
'
]
=
=
'
mobile
/
android
'
:
            
rc
=
self
.
check_java
(
source
jobs
strip
verbose
skip_export
=
True
)
        
return
rc
    
StaticAnalysisSubCommand
(
'
static
-
analysis
'
'
check
-
coverity
'
                              
'
Run
coverity
static
-
analysis
tool
on
the
given
files
.
'
                              
'
Can
only
be
run
by
automation
!
'
                              
'
It
\
'
s
result
is
stored
as
an
json
file
on
the
artifacts
server
.
'
)
    
CommandArgument
(
'
source
'
nargs
=
'
*
'
default
=
[
]
                     
help
=
'
Source
files
to
be
analyzed
by
Coverity
Static
Analysis
Tool
.
'
                          
'
This
is
ran
only
in
automation
.
'
)
    
CommandArgument
(
'
-
-
output
'
'
-
o
'
default
=
None
                     
help
=
'
Write
coverity
output
translated
to
json
output
in
a
file
'
)
    
CommandArgument
(
'
-
-
coverity_output_path
'
'
-
co
'
default
=
None
                     
help
=
'
Path
where
to
write
coverity
results
as
cov
-
results
.
json
.
'
                     
'
If
no
path
is
specified
the
default
path
from
the
coverity
working
'
                     
'
directory
~
.
/
mozbuild
/
coverity
is
used
.
'
)
    
CommandArgument
(
'
-
-
outgoing
'
default
=
False
action
=
'
store_true
'
                     
help
=
'
Run
coverity
on
outgoing
files
from
mercurial
or
git
repository
'
)
    
def
check_coverity
(
self
source
=
[
]
output
=
None
coverity_output_path
=
None
                       
outgoing
=
False
verbose
=
False
)
:
        
self
.
_set_log_level
(
verbose
)
        
self
.
log_manager
.
enable_all_structured_loggers
(
)
        
if
'
MOZ_AUTOMATION
'
not
in
os
.
environ
:
            
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                     
'
Coverity
based
static
-
analysis
cannot
be
ran
outside
automation
.
'
)
            
return
        
#
Use
outgoing
files
instead
of
source
files
        
if
outgoing
:
            
repo
=
get_repository_object
(
self
.
topsrcdir
)
            
files
=
repo
.
get_outgoing_files
(
)
            
source
=
map
(
os
.
path
.
abspath
files
)
        
if
len
(
source
)
=
=
0
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
'
There
are
no
files
that
coverity
can
use
to
scan
.
'
)
            
return
0
        
rc
=
self
.
_build_compile_db
(
verbose
=
verbose
)
        
rc
=
rc
or
self
.
_build_export
(
jobs
=
2
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
return
rc
        
commands_list
=
self
.
get_files_with_commands
(
source
)
        
if
len
(
commands_list
)
=
=
0
:
            
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                     
'
There
are
no
files
that
need
to
be
analyzed
.
'
)
            
return
0
        
#
Load
the
configuration
file
for
coverity
static
-
analysis
        
#
For
the
moment
we
store
only
the
reliability
index
for
each
checker
        
#
as
the
rest
is
managed
on
the
https
:
/
/
github
.
com
/
mozilla
/
release
-
services
side
.
        
self
.
_cov_config
=
self
.
_get_cov_config
(
)
        
rc
=
self
.
setup_coverity
(
)
        
if
rc
!
=
0
:
            
return
rc
        
#
First
run
cov
-
run
-
desktop
-
-
setup
in
order
to
setup
the
analysis
env
        
cmd
=
[
self
.
cov_run_desktop
'
-
-
setup
'
]
        
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                 
'
Running
{
}
-
-
setup
'
.
format
(
self
.
cov_run_desktop
)
)
        
rc
=
self
.
run_process
(
args
=
cmd
cwd
=
self
.
cov_path
pass_thru
=
True
)
        
if
rc
!
=
0
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
'
Running
{
}
-
-
setup
failed
!
'
.
format
(
self
.
cov_run_desktop
)
)
            
return
rc
        
#
Run
cov
-
configure
for
clang
        
cmd
=
[
self
.
cov_configure
'
-
-
clang
'
]
        
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                 
'
Running
{
}
-
-
clang
'
.
format
(
self
.
cov_configure
)
)
        
rc
=
self
.
run_process
(
args
=
cmd
cwd
=
self
.
cov_path
pass_thru
=
True
)
        
if
rc
!
=
0
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
'
Running
{
}
-
-
clang
failed
!
'
.
format
(
self
.
cov_configure
)
)
            
return
rc
        
#
For
each
element
in
commands_list
run
cov
-
translate
        
for
element
in
commands_list
:
            
cmd
=
[
self
.
cov_translate
'
-
-
dir
'
self
.
cov_idir_path
]
+
element
[
'
command
'
]
.
split
(
'
'
)
            
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                     
'
Running
Coverity
Tranlate
for
{
}
'
.
format
(
cmd
)
)
            
rc
=
self
.
run_process
(
args
=
cmd
cwd
=
element
[
'
directory
'
]
pass_thru
=
True
)
            
if
rc
!
=
0
:
                
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                         
'
Running
Coverity
Tranlate
failed
for
{
}
'
.
format
(
cmd
)
)
                
return
cmd
        
if
coverity_output_path
is
None
:
            
cov_result
=
mozpath
.
join
(
self
.
cov_state_path
'
cov
-
results
.
json
'
)
        
else
:
            
cov_result
=
mozpath
.
join
(
coverity_output_path
'
cov
-
results
.
json
'
)
        
#
Once
the
capture
is
performed
we
need
to
do
the
actual
Coverity
Desktop
analysis
        
cmd
=
[
self
.
cov_run_desktop
'
-
-
json
-
output
-
v6
'
cov_result
'
-
-
analyze
-
captured
-
source
'
]
        
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                 
'
Running
Coverity
Analysis
for
{
}
'
.
format
(
cmd
)
)
        
rc
=
self
.
run_process
(
cmd
cwd
=
self
.
cov_state_path
pass_thru
=
True
)
        
if
rc
!
=
0
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
'
Coverity
Analysis
failed
!
'
)
        
if
output
is
not
None
:
            
self
.
dump_cov_artifact
(
cov_result
source
output
)
    
def
get_reliability_index_for_cov_checker
(
self
checker_name
)
:
        
if
self
.
_cov_config
is
None
:
            
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
'
Coverity
config
file
not
found
'
                     
'
using
default
-
value
\
'
reliablity
\
'
=
medium
.
for
checker
{
}
'
.
format
(
                        
checker_name
)
)
            
return
'
medium
'
        
checkers
=
self
.
_cov_config
[
'
coverity_checkers
'
]
        
if
checker_name
not
in
checkers
:
            
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                     
'
Coverity
checker
{
}
not
found
to
determine
reliability
index
.
'
                     
'
For
the
moment
we
shall
use
the
default
\
'
reliablity
\
'
=
medium
.
'
.
format
(
                        
checker_name
)
)
            
return
'
medium
'
        
if
'
reliability
'
not
in
checkers
[
checker_name
]
:
            
#
This
checker
doesn
'
t
have
a
reliability
index
            
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                     
'
Coverity
checker
{
}
doesn
\
'
t
have
a
reliability
index
set
'
                     
'
field
\
'
reliability
is
missing
\
'
please
cosinder
adding
it
.
'
                     
'
For
the
moment
we
shall
use
the
default
\
'
reliablity
\
'
=
medium
.
'
.
format
(
                        
checker_name
)
)
            
return
'
medium
'
        
return
checkers
[
checker_name
]
[
'
reliability
'
]
    
def
dump_cov_artifact
(
self
cov_results
source
output
)
:
        
#
Parse
Coverity
json
into
structured
issues
        
with
open
(
cov_results
)
as
f
:
            
result
=
json
.
load
(
f
)
            
#
Parse
the
issues
to
a
standard
json
format
            
issues_dict
=
{
'
files
'
:
{
}
}
            
files_list
=
issues_dict
[
'
files
'
]
            
def
build_element
(
issue
)
:
                
#
We
look
only
for
main
event
                
event_path
=
next
(
                    
(
event
for
event
in
issue
[
'
events
'
]
if
event
[
'
main
'
]
is
True
)
None
)
                
dict_issue
=
{
                    
'
line
'
:
issue
[
'
mainEventLineNumber
'
]
                    
'
flag
'
:
issue
[
'
checkerName
'
]
                    
'
message
'
:
event_path
[
'
eventDescription
'
]
                    
'
reliability
'
:
self
.
get_reliability_index_for_cov_checker
(
                        
issue
[
'
checkerName
'
]
                        
)
                    
'
extra
'
:
{
                        
'
category
'
:
issue
[
'
checkerProperties
'
]
[
'
category
'
]
                        
'
stateOnServer
'
:
issue
[
'
stateOnServer
'
]
                        
'
stack
'
:
[
]
                    
}
                
}
                
#
Embed
all
events
into
extra
message
                
for
event
in
issue
[
'
events
'
]
:
                    
dict_issue
[
'
extra
'
]
[
'
stack
'
]
.
append
(
                        
{
'
file_path
'
:
event
[
'
strippedFilePathname
'
]
                         
'
line_number
'
:
event
[
'
lineNumber
'
]
                         
'
path_type
'
:
event
[
'
eventTag
'
]
                         
'
description
'
:
event
[
'
eventDescription
'
]
}
)
                
return
dict_issue
            
for
issue
in
result
[
'
issues
'
]
:
                
path
=
self
.
cov_is_file_in_source
(
issue
[
'
strippedMainEventFilePathname
'
]
source
)
                
if
path
is
None
:
                    
#
Since
we
skip
a
result
we
should
log
it
                    
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                             
'
Skipping
CID
:
{
0
}
from
file
:
{
1
}
since
it
\
'
s
not
related
'
                             
'
with
the
current
patch
.
'
.
format
(
                                
issue
[
'
stateOnServer
'
]
[
'
cid
'
]
                                
issue
[
'
strippedMainEventFilePathname
'
]
)
                             
)
                    
continue
                
if
path
in
files_list
:
                    
files_list
[
path
]
[
'
warnings
'
]
.
append
(
build_element
(
issue
)
)
                
else
:
                    
files_list
[
path
]
=
{
'
warnings
'
:
[
build_element
(
issue
)
]
}
            
with
open
(
output
'
w
'
)
as
f
:
                
json
.
dump
(
issues_dict
f
)
    
def
get_coverity_secrets
(
self
)
:
        
from
taskgraph
.
util
.
taskcluster
import
get_root_url
        
secret_name
=
'
project
/
relman
/
coverity
'
        
secrets_url
=
'
{
}
/
secrets
/
v1
/
secret
/
{
}
'
.
format
(
get_root_url
(
True
)
secret_name
)
        
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                 
'
Using
symbol
upload
token
from
the
secrets
service
:
"
{
}
"
'
.
format
(
secrets_url
)
)
        
import
requests
        
res
=
requests
.
get
(
secrets_url
)
        
res
.
raise_for_status
(
)
        
secret
=
res
.
json
(
)
        
cov_config
=
secret
[
'
secret
'
]
if
'
secret
'
in
secret
else
None
        
if
cov_config
is
None
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
'
Ill
formatted
secret
for
Coverity
.
Aborting
analysis
.
'
)
            
return
1
        
self
.
cov_analysis_url
=
cov_config
.
get
(
'
package_url
'
)
        
self
.
cov_package_name
=
cov_config
.
get
(
'
package_name
'
)
        
self
.
cov_url
=
cov_config
.
get
(
'
server_url
'
)
        
#
In
case
we
don
'
t
have
a
port
in
the
secret
we
use
the
default
one
        
#
for
a
default
coverity
deployment
.
        
self
.
cov_port
=
cov_config
.
get
(
'
server_port
'
8443
)
        
self
.
cov_auth
=
cov_config
.
get
(
'
auth_key
'
)
        
self
.
cov_package_ver
=
cov_config
.
get
(
'
package_ver
'
)
        
self
.
cov_full_stack
=
cov_config
.
get
(
'
full_stack
'
False
)
        
return
0
    
def
download_coverity
(
self
)
:
        
if
self
.
cov_url
is
None
or
self
.
cov_port
is
None
or
\
                
self
.
cov_analysis_url
is
None
or
\
                
self
.
cov_auth
is
None
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
'
Missing
Coverity
secret
on
try
job
!
'
)
            
return
1
        
COVERITY_CONFIG
=
'
'
'
        
{
            
"
type
"
:
"
Coverity
configuration
"
            
"
format_version
"
:
1
            
"
settings
"
:
{
            
"
server
"
:
{
                
"
host
"
:
"
%
s
"
                
"
ssl
"
:
true
                
"
port
"
:
%
s
                
"
on_new_cert
"
:
"
trust
"
                
"
auth_key_file
"
:
"
%
s
"
            
}
            
"
stream
"
:
"
Firefox
"
            
"
cov_run_desktop
"
:
{
                
"
build_cmd
"
:
[
]
                
"
clean_cmd
"
:
[
]
            
}
            
}
        
}
        
'
'
'
        
#
Generate
the
coverity
.
conf
and
auth
files
        
cov_auth_path
=
mozpath
.
join
(
self
.
cov_state_path
'
auth
'
)
        
cov_setup_path
=
mozpath
.
join
(
self
.
cov_state_path
'
coverity
.
conf
'
)
        
cov_conf
=
COVERITY_CONFIG
%
(
self
.
cov_url
self
.
cov_port
cov_auth_path
)
        
def
download
(
artifact_url
target
)
:
            
import
requests
            
resp
=
requests
.
get
(
artifact_url
verify
=
False
stream
=
True
)
            
resp
.
raise_for_status
(
)
            
#
Extract
archive
into
destination
            
with
tarfile
.
open
(
fileobj
=
io
.
BytesIO
(
resp
.
content
)
)
as
tar
:
                
tar
.
extractall
(
target
)
        
download
(
self
.
cov_analysis_url
self
.
cov_state_path
)
        
with
open
(
cov_auth_path
'
w
'
)
as
f
:
            
f
.
write
(
self
.
cov_auth
)
        
#
Modify
it
'
s
permission
to
600
        
os
.
chmod
(
cov_auth_path
0o600
)
        
with
open
(
cov_setup_path
'
a
'
)
as
f
:
            
f
.
write
(
cov_conf
)
    
def
setup_coverity
(
self
force_download
=
True
)
:
        
rc
config
_
=
self
.
_get_config_environment
(
)
        
rc
=
rc
or
self
.
get_coverity_secrets
(
)
        
if
rc
!
=
0
:
            
return
rc
        
#
Create
a
directory
in
mozbuild
where
we
setup
coverity
        
self
.
cov_state_path
=
mozpath
.
join
(
self
.
_mach_context
.
state_dir
"
coverity
"
)
        
if
force_download
is
True
and
os
.
path
.
exists
(
self
.
cov_state_path
)
:
            
shutil
.
rmtree
(
self
.
cov_state_path
)
        
os
.
mkdir
(
self
.
cov_state_path
)
        
#
Download
everything
that
we
need
for
Coverity
from
out
private
instance
        
self
.
download_coverity
(
)
        
self
.
cov_path
=
mozpath
.
join
(
self
.
cov_state_path
self
.
cov_package_name
)
        
self
.
cov_run_desktop
=
mozpath
.
join
(
self
.
cov_path
'
bin
'
'
cov
-
run
-
desktop
'
)
        
self
.
cov_translate
=
mozpath
.
join
(
self
.
cov_path
'
bin
'
'
cov
-
translate
'
)
        
self
.
cov_configure
=
mozpath
.
join
(
self
.
cov_path
'
bin
'
'
cov
-
configure
'
)
        
self
.
cov_work_path
=
mozpath
.
join
(
self
.
cov_state_path
'
data
-
coverity
'
)
        
self
.
cov_idir_path
=
mozpath
.
join
(
self
.
cov_work_path
self
.
cov_package_ver
'
idir
'
)
        
if
not
os
.
path
.
exists
(
self
.
cov_path
)
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
'
Missing
Coverity
in
{
}
'
.
format
(
self
.
cov_path
)
)
            
return
1
        
return
0
    
def
cov_is_file_in_source
(
self
abs_path
source
)
:
        
#
We
have
as
an
input
an
absolute
path
for
whom
we
verify
if
it
'
s
a
symlink
        
#
if
so
we
follow
that
symlink
and
we
match
it
with
elements
from
source
.
        
#
If
the
match
is
done
we
return
abs_path
otherwise
None
        
assert
isinstance
(
source
list
)
        
if
os
.
path
.
islink
(
abs_path
)
:
            
abs_path
=
os
.
path
.
realpath
(
abs_path
)
        
if
abs_path
in
source
:
            
return
abs_path
        
return
None
    
def
get_files_with_commands
(
self
source
)
:
        
'
'
'
        
Returns
an
array
of
dictionaries
having
file_path
with
build
command
        
'
'
'
        
compile_db
=
json
.
load
(
open
(
self
.
_compile_db
'
r
'
)
)
        
commands_list
=
[
]
        
for
f
in
source
:
            
#
It
must
be
a
C
/
C
+
+
file
            
_
ext
=
os
.
path
.
splitext
(
f
)
            
if
ext
.
lower
(
)
not
in
self
.
_format_include_extensions
:
                
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
'
Skipping
{
}
'
.
format
(
f
)
)
                
continue
            
file_with_abspath
=
os
.
path
.
join
(
self
.
topsrcdir
f
)
            
for
f
in
compile_db
:
                
#
Found
for
a
file
that
we
are
looking
                
if
file_with_abspath
=
=
f
[
'
file
'
]
:
                    
commands_list
.
append
(
f
)
        
return
commands_list
    
StaticAnalysisSubCommand
(
'
static
-
analysis
'
'
check
-
java
'
                              
'
Run
infer
on
the
java
codebase
.
'
)
    
CommandArgument
(
'
source
'
nargs
=
'
*
'
default
=
[
'
mobile
'
]
                     
help
=
'
Source
files
to
be
analyzed
.
'
                          
'
Can
be
omitted
in
which
case
the
entire
code
base
'
                          
'
is
analyzed
.
The
source
argument
is
ignored
if
'
                          
'
there
is
anything
fed
through
stdin
in
which
case
'
                          
'
the
analysis
is
only
performed
on
the
files
changed
'
                          
'
in
the
patch
streamed
through
stdin
.
This
is
called
'
                          
'
the
diff
mode
.
'
)
    
CommandArgument
(
'
-
-
checks
'
'
-
c
'
default
=
[
]
metavar
=
'
checks
'
nargs
=
'
*
'
                     
help
=
'
Static
analysis
checks
to
enable
.
'
)
    
CommandArgument
(
'
-
-
jobs
'
'
-
j
'
default
=
'
0
'
metavar
=
'
jobs
'
type
=
int
                     
help
=
'
Number
of
concurrent
jobs
to
run
.
'
                     
'
Default
is
the
number
of
CPUs
.
'
)
    
CommandArgument
(
'
-
-
task
'
'
-
t
'
type
=
str
                     
default
=
'
compileWithGeckoBinariesDebugSources
'
                     
help
=
'
Which
gradle
tasks
to
use
to
compile
the
java
codebase
.
'
)
    
CommandArgument
(
'
-
-
outgoing
'
default
=
False
action
=
'
store_true
'
                     
help
=
'
Run
infer
checks
on
outgoing
files
from
repository
'
)
    
CommandArgument
(
'
-
-
output
'
default
=
None
                     
help
=
'
Write
infer
json
output
in
a
file
'
)
    
def
check_java
(
self
source
=
[
'
mobile
'
]
jobs
=
2
strip
=
1
verbose
=
False
checks
=
[
]
                   
task
=
'
compileWithGeckoBinariesDebugSources
'
                   
skip_export
=
False
outgoing
=
False
output
=
None
)
:
        
self
.
_set_log_level
(
verbose
)
        
self
.
log_manager
.
enable_all_structured_loggers
(
)
        
if
self
.
substs
[
'
MOZ_BUILD_APP
'
]
!
=
'
mobile
/
android
'
:
            
self
.
log
(
logging
.
WARNING
'
static
-
analysis
'
{
}
                     
'
Cannot
check
java
source
code
unless
you
are
building
for
android
!
'
)
            
return
1
        
rc
=
self
.
_check_for_java
(
)
        
if
rc
!
=
0
:
            
return
1
        
if
output
is
not
None
:
            
output
=
os
.
path
.
abspath
(
output
)
            
if
not
os
.
path
.
isdir
(
os
.
path
.
dirname
(
output
)
)
:
                
self
.
log
(
logging
.
WARNING
'
static
-
analysis
'
{
}
                         
'
Missing
report
destination
folder
for
{
}
'
.
format
(
output
)
)
        
#
if
source
contains
the
whole
mobile
folder
then
we
just
have
to
        
#
analyze
everything
        
check_all
=
any
(
i
.
rstrip
(
os
.
sep
)
.
split
(
os
.
sep
)
[
-
1
]
=
=
'
mobile
'
for
i
in
source
)
        
#
gather
all
java
sources
from
the
source
variable
        
java_sources
=
[
]
        
if
outgoing
:
            
repo
=
get_repository_object
(
self
.
topsrcdir
)
            
java_sources
=
self
.
_get_java_files
(
repo
.
get_outgoing_files
(
)
)
            
if
not
java_sources
:
                
self
.
log
(
logging
.
WARNING
'
static
-
analysis
'
{
}
                         
'
No
outgoing
Java
files
to
check
'
)
                
return
0
        
elif
not
check_all
:
            
java_sources
=
self
.
_get_java_files
(
source
)
            
if
not
java_sources
:
                
return
0
        
if
not
skip_export
:
            
rc
=
self
.
_build_export
(
jobs
=
jobs
verbose
=
verbose
)
            
if
rc
!
=
0
:
                
return
rc
        
rc
=
self
.
_get_infer
(
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
self
.
log
(
logging
.
WARNING
'
static
-
analysis
'
{
}
                     
'
This
command
is
only
available
for
linux64
!
'
)
            
return
rc
        
#
which
checkers
to
use
and
which
folders
to
exclude
        
all_checkers
third_party_path
=
self
.
_get_infer_config
(
)
        
checkers
excludes
=
self
.
_get_infer_args
(
            
checks
=
checks
or
all_checkers
            
third_party_path
=
third_party_path
        
)
        
rc
=
rc
or
self
.
_gradle
(
[
'
clean
'
]
)
#
clean
so
that
we
can
recompile
        
#
infer
capture
command
        
capture_cmd
=
[
self
.
_infer_path
'
capture
'
]
+
excludes
+
[
'
-
-
'
]
        
rc
=
rc
or
self
.
_gradle
(
[
task
]
infer_args
=
capture_cmd
verbose
=
verbose
)
        
tmp_file
args
=
self
.
_get_infer_source_args
(
java_sources
)
        
#
infer
analyze
command
        
analysis_cmd
=
[
self
.
_infer_path
'
analyze
'
'
-
-
keep
-
going
'
]
+
\
            
checkers
+
args
        
rc
=
rc
or
self
.
run_process
(
args
=
analysis_cmd
cwd
=
self
.
topsrcdir
pass_thru
=
True
)
        
if
tmp_file
:
            
tmp_file
.
close
(
)
        
#
Copy
the
infer
report
        
report_path
=
os
.
path
.
join
(
self
.
topsrcdir
'
infer
-
out
'
'
report
.
json
'
)
        
if
output
is
not
None
and
os
.
path
.
exists
(
report_path
)
:
            
shutil
.
copy
(
report_path
output
)
            
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                     
'
Report
available
in
{
}
'
.
format
(
output
)
)
        
return
rc
    
def
_get_java_files
(
self
sources
)
:
        
java_sources
=
[
]
        
for
i
in
sources
:
            
f
=
mozpath
.
join
(
self
.
topsrcdir
i
)
            
if
os
.
path
.
isdir
(
f
)
:
                
for
root
dirs
files
in
os
.
walk
(
f
)
:
                    
dirs
.
sort
(
)
                    
for
file
in
sorted
(
files
)
:
                        
if
file
.
endswith
(
'
.
java
'
)
:
                            
java_sources
.
append
(
mozpath
.
join
(
root
file
)
)
            
elif
f
.
endswith
(
'
.
java
'
)
:
                
java_sources
.
append
(
f
)
        
return
java_sources
    
def
_get_infer_source_args
(
self
sources
)
:
        
'
'
'
Return
the
arguments
to
only
analyze
<
sources
>
'
'
'
        
if
not
sources
:
            
return
(
None
[
]
)
        
#
create
a
temporary
file
in
which
we
place
all
sources
        
#
this
is
used
by
the
analysis
command
to
only
analyze
certain
files
        
f
=
tempfile
.
NamedTemporaryFile
(
)
        
for
source
in
sources
:
            
f
.
write
(
source
+
'
\
n
'
)
        
f
.
flush
(
)
        
return
(
f
[
'
-
-
changed
-
files
-
index
'
f
.
name
]
)
    
def
_get_infer_config
(
self
)
:
        
'
'
'
Load
the
infer
config
file
.
'
'
'
        
checkers
=
[
]
        
tp_path
=
'
'
        
with
open
(
mozpath
.
join
(
self
.
topsrcdir
'
tools
'
                               
'
infer
'
'
config
.
yaml
'
)
)
as
f
:
            
try
:
                
config
=
yaml
.
safe_load
(
f
)
                
for
item
in
config
[
'
infer_checkers
'
]
:
                    
if
item
[
'
publish
'
]
:
                        
checkers
.
append
(
item
[
'
name
'
]
)
                
tp_path
=
mozpath
.
join
(
self
.
topsrcdir
config
[
'
third_party
'
]
)
            
except
Exception
:
                
print
(
'
Looks
like
config
.
yaml
is
not
valid
so
we
are
unable
'
                      
'
to
determine
default
checkers
and
which
folder
to
'
                      
'
exclude
using
defaults
provided
by
infer
'
)
        
return
checkers
tp_path
    
def
_get_infer_args
(
self
checks
third_party_path
)
:
        
'
'
'
Return
the
arguments
which
include
the
checkers
<
checks
>
and
        
excludes
all
folder
in
<
third_party_path
>
.
'
'
'
        
checkers
=
[
'
-
a
'
'
checkers
'
]
        
excludes
=
[
]
        
for
checker
in
checks
:
            
checkers
.
append
(
'
-
-
'
+
checker
)
        
with
open
(
third_party_path
)
as
f
:
            
for
line
in
f
:
                
excludes
.
append
(
'
-
-
skip
-
analysis
-
in
-
path
'
)
                
excludes
.
append
(
line
.
strip
(
'
\
n
'
)
)
        
return
checkers
excludes
    
def
_get_clang_tidy_config
(
self
)
:
        
try
:
            
file_handler
=
open
(
mozpath
.
join
(
self
.
topsrcdir
"
tools
"
"
clang
-
tidy
"
"
config
.
yaml
"
)
)
            
config
=
yaml
.
safe_load
(
file_handler
)
        
except
Exception
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
'
Looks
like
config
.
yaml
is
not
valid
we
are
going
to
use
default
'
                     
'
values
for
the
rest
of
the
analysis
for
clang
-
tidy
.
'
)
            
return
None
        
return
config
    
def
_get_cov_config
(
self
)
:
        
try
:
            
file_handler
=
open
(
mozpath
.
join
(
self
.
topsrcdir
"
tools
"
"
coverity
"
"
config
.
yaml
"
)
)
            
config
=
yaml
.
safe_load
(
file_handler
)
        
except
Exception
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
'
Looks
like
config
.
yaml
is
not
valid
we
are
going
to
use
default
'
                     
'
values
for
the
rest
of
the
analysis
for
coverity
.
'
)
            
return
None
        
return
config
    
def
_is_version_eligible
(
self
)
:
        
#
make
sure
that
we
'
ve
cached
self
.
_clang_tidy_config
        
if
self
.
_clang_tidy_config
is
None
:
            
self
.
_clang_tidy_config
=
self
.
_get_clang_tidy_config
(
)
        
version
=
None
        
if
'
package_version
'
in
self
.
_clang_tidy_config
:
            
version
=
self
.
_clang_tidy_config
[
'
package_version
'
]
        
else
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
"
Unable
to
find
'
package_version
'
in
the
config
.
yml
"
)
            
return
False
        
#
Because
the
fact
that
we
ship
together
clang
-
tidy
and
clang
-
format
        
#
we
are
sure
that
these
two
will
always
share
the
same
version
.
        
#
Thus
in
order
to
determine
that
the
version
is
compatible
we
only
        
#
need
to
check
one
of
them
going
with
clang
-
format
        
cmd
=
[
self
.
_clang_format_path
'
-
-
version
'
]
        
try
:
            
output
=
subprocess
.
check_output
(
cmd
stderr
=
subprocess
.
STDOUT
)
.
decode
(
'
utf
-
8
'
)
            
version_string
=
'
clang
-
format
version
'
+
version
            
if
output
.
startswith
(
version_string
)
:
                
return
True
        
except
subprocess
.
CalledProcessError
as
e
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
"
Error
determining
the
version
clang
-
tidy
/
format
binary
please
see
the
"
                     
"
attached
exception
:
\
n
{
}
"
.
format
(
e
.
output
)
)
        
return
False
    
def
_get_clang_tidy_command
(
self
checks
header_filter
sources
jobs
fix
)
:
        
if
checks
=
=
'
-
*
'
:
            
checks
=
self
.
_get_checks
(
)
        
common_args
=
[
'
-
clang
-
tidy
-
binary
'
self
.
_clang_tidy_path
                       
'
-
clang
-
apply
-
replacements
-
binary
'
self
.
_clang_apply_replacements
                       
'
-
checks
=
%
s
'
%
checks
                       
'
-
extra
-
arg
=
-
DMOZ_CLANG_PLUGIN
'
]
        
#
Flag
header
-
filter
is
passed
in
order
to
limit
the
diagnostic
messages
only
        
#
to
the
specified
header
files
.
When
no
value
is
specified
the
default
value
        
#
is
considered
to
be
the
source
in
order
to
limit
the
diagnostic
message
to
        
#
the
source
files
or
folders
.
        
common_args
+
=
[
'
-
header
-
filter
=
%
s
'
%
(
header_filter
                                               
if
len
(
header_filter
)
else
'
|
'
.
join
(
sources
)
)
]
        
#
From
our
configuration
file
config
.
yaml
we
build
the
configuration
list
for
        
#
the
checkers
that
are
used
.
These
configuration
options
are
used
to
better
fit
        
#
the
checkers
to
our
code
.
        
cfg
=
self
.
_get_checks_config
(
)
        
if
cfg
:
            
common_args
+
=
[
'
-
config
=
%
s
'
%
yaml
.
dump
(
cfg
)
]
        
if
fix
:
            
common_args
+
=
[
'
-
fix
'
]
        
return
[
            
self
.
virtualenv_manager
.
python_path
self
.
_run_clang_tidy_path
'
-
j
'
            
str
(
jobs
)
'
-
p
'
self
.
_compilation_commands_path
        
]
+
common_args
+
sources
    
def
_check_for_java
(
self
)
:
        
'
'
'
Check
if
javac
can
be
found
.
'
'
'
        
import
distutils
        
java
=
self
.
substs
.
get
(
'
JAVA
'
)
        
java
=
java
or
os
.
getenv
(
'
JAVA_HOME
'
)
        
java
=
java
or
distutils
.
spawn
.
find_executable
(
'
javac
'
)
        
error
=
'
javac
was
not
found
!
Please
install
javac
and
either
add
it
to
your
PATH
'
        
error
+
=
'
set
JAVA_HOME
or
add
the
following
to
your
mozconfig
:
\
n
'
        
error
+
=
'
-
-
with
-
java
-
bin
-
path
=
/
path
/
to
/
java
/
bin
/
'
        
if
not
java
:
            
self
.
log
(
logging
.
ERROR
'
ERROR
:
static
-
analysis
'
{
}
error
)
            
return
1
        
return
0
    
def
_gradle
(
self
args
infer_args
=
None
verbose
=
False
autotest
=
False
                
suppress_output
=
True
)
:
        
infer_args
=
infer_args
or
[
]
        
if
autotest
:
            
cwd
=
mozpath
.
join
(
self
.
topsrcdir
'
tools
'
'
infer
'
'
test
'
)
            
gradle
=
mozpath
.
join
(
cwd
'
gradlew
'
)
        
else
:
            
gradle
=
self
.
substs
[
'
GRADLE
'
]
            
cwd
=
self
.
topsrcdir
        
extra_env
=
{
            
'
GRADLE_OPTS
'
:
'
-
Dfile
.
encoding
=
utf
-
8
'
#
see
mobile
/
android
/
mach_commands
.
py
            
'
JAVA_TOOL_OPTIONS
'
:
'
-
Dfile
.
encoding
=
utf
-
8
'
        
}
        
if
suppress_output
:
            
devnull
=
open
(
os
.
devnull
'
w
'
)
            
return
subprocess
.
call
(
                
infer_args
+
[
gradle
]
+
args
                
env
=
dict
(
os
.
environ
*
*
extra_env
)
                
cwd
=
cwd
stdout
=
devnull
stderr
=
subprocess
.
STDOUT
close_fds
=
True
)
        
return
self
.
run_process
(
            
infer_args
+
[
gradle
]
+
args
            
append_env
=
extra_env
            
pass_thru
=
True
#
Allow
user
to
run
gradle
interactively
.
            
ensure_exit_code
=
False
#
Don
'
t
throw
on
non
-
zero
exit
code
.
            
cwd
=
cwd
)
    
StaticAnalysisSubCommand
(
'
static
-
analysis
'
'
autotest
'
                              
'
Run
the
auto
-
test
suite
in
order
to
determine
that
'
                              
'
the
analysis
did
not
regress
.
'
)
    
CommandArgument
(
'
-
-
dump
-
results
'
'
-
d
'
default
=
False
action
=
'
store_true
'
                     
help
=
'
Generate
the
baseline
for
the
regression
test
.
Based
on
'
                     
'
this
baseline
we
will
test
future
results
.
'
)
    
CommandArgument
(
'
-
-
intree
-
tool
'
'
-
i
'
default
=
False
action
=
'
store_true
'
                     
help
=
'
Use
a
pre
-
aquired
in
-
tree
clang
-
tidy
package
.
'
)
    
CommandArgument
(
'
checker_names
'
nargs
=
'
*
'
default
=
[
]
                     
help
=
'
Checkers
that
are
going
to
be
auto
-
tested
.
'
)
    
def
autotest
(
self
verbose
=
False
dump_results
=
False
intree_tool
=
False
checker_names
=
[
]
)
:
        
#
If
'
dump_results
'
is
True
than
we
just
want
to
generate
the
issues
files
for
each
        
#
checker
in
particulat
and
thus
'
force_download
'
becomes
'
False
'
since
we
want
to
        
#
do
this
on
a
local
trusted
clang
-
tidy
package
.
        
self
.
_set_log_level
(
verbose
)
        
self
.
_dump_results
=
dump_results
        
force_download
=
not
self
.
_dump_results
        
#
Function
return
codes
        
self
.
TOOLS_SUCCESS
=
0
        
self
.
TOOLS_FAILED_DOWNLOAD
=
1
        
self
.
TOOLS_UNSUPORTED_PLATFORM
=
2
        
self
.
TOOLS_CHECKER_NO_TEST_FILE
=
3
        
self
.
TOOLS_CHECKER_RETURNED_NO_ISSUES
=
4
        
self
.
TOOLS_CHECKER_RESULT_FILE_NOT_FOUND
=
5
        
self
.
TOOLS_CHECKER_DIFF_FAILED
=
6
        
self
.
TOOLS_CHECKER_NOT_FOUND
=
7
        
self
.
TOOLS_CHECKER_FAILED_FILE
=
8
        
self
.
TOOLS_CHECKER_LIST_EMPTY
=
9
        
self
.
TOOLS_GRADLE_FAILED
=
10
        
#
Configure
the
tree
or
download
clang
-
tidy
package
depending
on
the
option
that
we
choose
        
if
intree_tool
:
            
_
config
_
=
self
.
_get_config_environment
(
)
            
clang_tools_path
=
self
.
topsrcdir
            
self
.
_clang_tidy_path
=
mozpath
.
join
(
                
clang_tools_path
"
clang
-
tidy
"
"
bin
"
                
"
clang
-
tidy
"
+
config
.
substs
.
get
(
'
BIN_SUFFIX
'
'
'
)
)
            
self
.
_clang_format_path
=
mozpath
.
join
(
                
clang_tools_path
"
clang
-
tidy
"
"
bin
"
                
"
clang
-
format
"
+
config
.
substs
.
get
(
'
BIN_SUFFIX
'
'
'
)
)
            
self
.
_clang_apply_replacements
=
mozpath
.
join
(
                
clang_tools_path
"
clang
-
tidy
"
"
bin
"
                
"
clang
-
apply
-
replacements
"
+
config
.
substs
.
get
(
'
BIN_SUFFIX
'
'
'
)
)
            
self
.
_run_clang_tidy_path
=
mozpath
.
join
(
clang_tools_path
"
clang
-
tidy
"
"
share
"
                                                     
"
clang
"
"
run
-
clang
-
tidy
.
py
"
)
            
self
.
_clang_format_diff
=
mozpath
.
join
(
clang_tools_path
"
clang
-
tidy
"
"
share
"
                                                   
"
clang
"
"
clang
-
format
-
diff
.
py
"
)
            
#
Ensure
that
clang
-
tidy
is
present
            
rc
=
not
os
.
path
.
exists
(
self
.
_clang_tidy_path
)
        
else
:
            
rc
=
self
.
_get_clang_tools
(
force
=
force_download
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
self
.
log
(
logging
.
ERROR
'
ERROR
:
static
-
analysis
'
{
}
                     
'
clang
-
tidy
unable
to
locate
package
.
'
)
            
return
self
.
TOOLS_FAILED_DOWNLOAD
        
self
.
_clang_tidy_base_path
=
mozpath
.
join
(
self
.
topsrcdir
"
tools
"
"
clang
-
tidy
"
)
        
#
For
each
checker
run
it
        
self
.
_clang_tidy_config
=
self
.
_get_clang_tidy_config
(
)
        
platform
_
=
self
.
platform
        
if
platform
not
in
self
.
_clang_tidy_config
[
'
platforms
'
]
:
            
self
.
log
(
                
logging
.
ERROR
'
static
-
analysis
'
{
}
                
"
RUNNING
:
clang
-
tidy
autotest
for
platform
{
}
not
supported
.
"
.
format
(
                    
platform
)
                
)
            
return
self
.
TOOLS_UNSUPORTED_PLATFORM
        
import
concurrent
.
futures
        
import
multiprocessing
        
max_workers
=
multiprocessing
.
cpu_count
(
)
        
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                 
"
RUNNING
:
clang
-
tidy
autotest
for
platform
{
0
}
with
{
1
}
workers
.
"
.
format
(
                     
platform
max_workers
)
)
        
#
List
all
available
checkers
        
cmd
=
[
self
.
_clang_tidy_path
'
-
list
-
checks
'
'
-
checks
=
*
'
]
        
clang_output
=
subprocess
.
check_output
(
            
cmd
stderr
=
subprocess
.
STDOUT
)
.
decode
(
'
utf
-
8
'
)
        
available_checks
=
clang_output
.
split
(
'
\
n
'
)
[
1
:
]
        
self
.
_clang_tidy_checks
=
[
c
.
strip
(
)
for
c
in
available_checks
if
c
]
        
#
Build
the
dummy
compile_commands
.
json
        
self
.
_compilation_commands_path
=
self
.
_create_temp_compilation_db
(
self
.
_clang_tidy_config
)
        
checkers_test_batch
=
[
]
        
checkers_results
=
[
]
        
with
concurrent
.
futures
.
ThreadPoolExecutor
(
max_workers
=
max_workers
)
as
executor
:
            
futures
=
[
]
            
for
item
in
self
.
_clang_tidy_config
[
'
clang_checkers
'
]
:
                
#
Skip
if
any
of
the
following
statements
is
true
:
                
#
1
.
Checker
attribute
'
publish
'
is
False
.
                
not_published
=
not
bool
(
item
.
get
(
'
publish
'
True
)
)
                
#
2
.
Checker
has
restricted
-
platforms
and
current
platform
is
not
of
them
.
                
ignored_platform
=
(
'
restricted
-
platforms
'
in
item
and
                                    
platform
not
in
item
[
'
restricted
-
platforms
'
]
)
                
#
3
.
Checker
name
is
mozilla
-
*
or
-
*
.
                
ignored_checker
=
item
[
'
name
'
]
in
[
'
mozilla
-
*
'
'
-
*
'
]
                
#
4
.
List
checker_names
is
passed
and
the
current
checker
is
not
part
of
the
                
#
list
or
'
publish
'
is
False
                
checker_not_in_list
=
checker_names
and
(
                    
item
[
'
name
'
]
not
in
checker_names
or
not_published
)
                
if
not_published
or
\
                   
ignored_platform
or
\
                   
ignored_checker
or
\
                   
checker_not_in_list
:
                    
continue
                
checkers_test_batch
.
append
(
item
[
'
name
'
]
)
                
futures
.
append
(
executor
.
submit
(
self
.
_verify_checker
item
checkers_results
)
)
            
error_code
=
self
.
TOOLS_SUCCESS
            
for
future
in
concurrent
.
futures
.
as_completed
(
futures
)
:
                
#
Wait
for
every
task
to
finish
                
ret_val
=
future
.
result
(
)
                
if
ret_val
!
=
self
.
TOOLS_SUCCESS
:
                    
#
We
are
interested
only
in
one
error
and
we
don
'
t
break
                    
#
the
execution
of
for
loop
since
we
want
to
make
sure
that
all
                    
#
tasks
finished
.
                    
error_code
=
ret_val
            
if
error_code
!
=
self
.
TOOLS_SUCCESS
:
                
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                         
"
FAIL
:
the
following
clang
-
tidy
check
(
s
)
failed
:
"
)
                
for
failure
in
checkers_results
:
                    
checker_error
=
failure
[
'
checker
-
error
'
]
                    
checker_name
=
failure
[
'
checker
-
name
'
]
                    
info1
=
failure
[
'
info1
'
]
                    
info2
=
failure
[
'
info2
'
]
                    
info3
=
failure
[
'
info3
'
]
                    
message_to_log
=
'
'
                    
if
checker_error
=
=
self
.
TOOLS_CHECKER_NOT_FOUND
:
                        
message_to_log
=
\
                            
"
\
tChecker
{
}
not
present
in
this
clang
-
tidy
version
.
"
.
format
(
                                
checker_name
)
                    
elif
checker_error
=
=
self
.
TOOLS_CHECKER_NO_TEST_FILE
:
                        
message_to_log
=
\
                            
"
\
tChecker
{
0
}
does
not
have
a
test
file
-
{
0
}
.
cpp
"
.
format
(
                                
checker_name
)
                    
elif
checker_error
=
=
self
.
TOOLS_CHECKER_RETURNED_NO_ISSUES
:
                        
message_to_log
=
(
                            
"
\
tChecker
{
0
}
did
not
find
any
issues
in
its
test
file
"
                            
"
clang
-
tidy
output
for
the
run
is
:
\
n
{
1
}
"
                            
)
.
format
(
checker_name
info1
)
                    
elif
checker_error
=
=
self
.
TOOLS_CHECKER_RESULT_FILE_NOT_FOUND
:
                        
message_to_log
=
\
                            
"
\
tChecker
{
0
}
does
not
have
a
result
file
-
{
0
}
.
json
"
.
format
(
                                
checker_name
)
                    
elif
checker_error
=
=
self
.
TOOLS_CHECKER_DIFF_FAILED
:
                        
message_to_log
=
(
                            
"
\
tChecker
{
0
}
\
nExpected
:
{
1
}
\
n
"
                            
"
Got
:
{
2
}
\
n
"
                            
"
clang
-
tidy
output
for
the
run
is
:
\
n
"
                            
"
{
3
}
"
                            
)
.
format
(
checker_name
info1
info2
info3
)
                    
print
(
'
\
n
'
+
message_to_log
)
                
#
Also
delete
the
tmp
folder
                
shutil
.
rmtree
(
self
.
_compilation_commands_path
)
                
return
error_code
            
#
Run
the
analysis
on
all
checkers
at
the
same
time
only
if
we
don
'
t
dump
results
.
            
if
not
self
.
_dump_results
:
                
ret_val
=
self
.
_run_analysis_batch
(
checkers_test_batch
)
                
if
ret_val
!
=
self
.
TOOLS_SUCCESS
:
                    
shutil
.
rmtree
(
self
.
_compilation_commands_path
)
                    
return
ret_val
        
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
"
SUCCESS
:
clang
-
tidy
all
tests
passed
.
"
)
        
#
Also
delete
the
tmp
folder
        
shutil
.
rmtree
(
self
.
_compilation_commands_path
)
        
return
self
.
_autotest_infer
(
intree_tool
force_download
verbose
)
    
def
_run_analysis
(
self
checks
header_filter
sources
jobs
=
1
fix
=
False
print_out
=
False
)
:
        
cmd
=
self
.
_get_clang_tidy_command
(
            
checks
=
checks
header_filter
=
header_filter
            
sources
=
sources
            
jobs
=
jobs
fix
=
fix
)
        
try
:
            
clang_output
=
subprocess
.
check_output
(
cmd
stderr
=
subprocess
.
STDOUT
)
.
decode
(
'
utf
-
8
'
)
        
except
subprocess
.
CalledProcessError
as
e
:
            
print
(
e
.
output
)
            
return
None
        
return
self
.
_parse_issues
(
clang_output
)
clang_output
    
def
_run_analysis_batch
(
self
items
)
:
        
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                 
"
RUNNING
:
clang
-
tidy
checker
batch
analysis
.
"
)
        
if
not
len
(
items
)
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
"
ERROR
:
clang
-
tidy
checker
list
is
empty
!
"
)
            
return
self
.
TOOLS_CHECKER_LIST_EMPTY
        
issues
clang_output
=
self
.
_run_analysis
(
            
checks
=
'
-
*
'
+
"
"
.
join
(
items
)
            
header_filter
=
'
'
            
sources
=
[
mozpath
.
join
(
self
.
_clang_tidy_base_path
"
test
"
checker
)
+
'
.
cpp
'
                     
for
checker
in
items
]
            
print_out
=
True
)
        
if
issues
is
None
:
            
return
self
.
TOOLS_CHECKER_FAILED_FILE
        
failed_checks
=
[
]
        
failed_checks_baseline
=
[
]
        
for
checker
in
items
:
            
test_file_path_json
=
mozpath
.
join
(
                
self
.
_clang_tidy_base_path
"
test
"
checker
)
+
'
.
json
'
            
#
Read
the
pre
-
determined
issues
            
baseline_issues
=
self
.
_get_autotest_stored_issues
(
test_file_path_json
)
            
#
We
also
stored
the
'
reliability
'
index
so
strip
that
from
the
baseline_issues
            
baseline_issues
[
:
]
=
[
item
for
item
in
baseline_issues
if
'
reliability
'
not
in
item
]
            
found
=
all
(
[
element_base
in
issues
for
element_base
in
baseline_issues
]
)
            
if
not
found
:
                
failed_checks
.
append
(
checker
)
                
failed_checks_baseline
.
append
(
baseline_issues
)
        
if
len
(
failed_checks
)
>
0
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
'
The
following
check
(
s
)
failed
for
bulk
analysis
:
'
+
'
'
.
join
(
failed_checks
)
)
            
for
failed_check
baseline_issue
in
zip
(
failed_checks
failed_checks_baseline
)
:
                
print
(
'
\
tChecker
{
0
}
expect
following
results
:
\
n
\
t
\
t
{
1
}
'
.
format
(
                    
failed_check
baseline_issue
)
)
            
print
(
'
This
is
the
output
generated
by
clang
-
tidy
for
the
bulk
build
:
\
n
{
}
'
.
format
(
                
clang_output
)
)
            
return
self
.
TOOLS_CHECKER_DIFF_FAILED
        
return
self
.
TOOLS_SUCCESS
    
def
_create_temp_compilation_db
(
self
config
)
:
        
directory
=
tempfile
.
mkdtemp
(
prefix
=
'
cc
'
)
        
with
open
(
mozpath
.
join
(
directory
"
compile_commands
.
json
"
)
"
wb
"
)
as
file_handler
:
            
compile_commands
=
[
]
            
director
=
mozpath
.
join
(
self
.
topsrcdir
'
tools
'
'
clang
-
tidy
'
'
test
'
)
            
for
item
in
config
[
'
clang_checkers
'
]
:
                
if
item
[
'
name
'
]
in
[
'
-
*
'
'
mozilla
-
*
'
]
:
                    
continue
                
file
=
item
[
'
name
'
]
+
'
.
cpp
'
                
element
=
{
}
                
element
[
"
directory
"
]
=
director
                
element
[
"
command
"
]
=
'
cpp
'
+
file
                
element
[
"
file
"
]
=
mozpath
.
join
(
director
file
)
                
compile_commands
.
append
(
element
)
            
json
.
dump
(
compile_commands
file_handler
)
            
file_handler
.
flush
(
)
            
return
directory
    
def
_autotest_infer
(
self
intree_tool
force_download
verbose
)
:
        
#
infer
is
not
available
on
other
platforms
but
autotest
should
work
even
without
        
#
it
being
installed
        
if
self
.
platform
[
0
]
=
=
'
linux64
'
:
            
rc
=
self
.
_check_for_java
(
)
            
if
rc
!
=
0
:
                
return
1
            
rc
=
self
.
_get_infer
(
force
=
force_download
verbose
=
verbose
intree_tool
=
intree_tool
)
            
if
rc
!
=
0
:
                
self
.
log
(
logging
.
ERROR
'
ERROR
:
static
-
analysis
'
{
}
                         
'
infer
unable
to
locate
package
.
'
)
                
return
self
.
TOOLS_FAILED_DOWNLOAD
            
self
.
__infer_tool
=
mozpath
.
join
(
self
.
topsrcdir
'
tools
'
'
infer
'
)
            
self
.
__infer_test_folder
=
mozpath
.
join
(
self
.
__infer_tool
'
test
'
)
            
import
concurrent
.
futures
            
import
multiprocessing
            
max_workers
=
multiprocessing
.
cpu_count
(
)
            
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                     
"
RUNNING
:
infer
autotest
for
platform
{
0
}
with
{
1
}
workers
.
"
.
format
(
                         
self
.
platform
[
0
]
max_workers
)
)
            
#
clean
previous
autotest
if
it
exists
            
rc
=
self
.
_gradle
(
[
'
autotest
:
clean
'
]
autotest
=
True
)
            
if
rc
!
=
0
:
                
return
rc
            
import
yaml
            
with
open
(
mozpath
.
join
(
self
.
__infer_tool
'
config
.
yaml
'
)
)
as
f
:
                
config
=
yaml
.
safe_load
(
f
)
            
with
concurrent
.
futures
.
ThreadPoolExecutor
(
max_workers
=
max_workers
)
as
executor
:
                
futures
=
[
]
                
for
item
in
config
[
'
infer_checkers
'
]
:
                    
if
item
[
'
publish
'
]
:
                        
futures
.
append
(
executor
.
submit
(
self
.
_verify_infer_checker
item
)
)
                
#
this
is
always
included
in
check
-
java
but
not
in
config
.
yaml
                
futures
.
append
(
executor
.
submit
(
self
.
_verify_infer_checker
                                               
{
'
name
'
:
'
checkers
'
}
)
)
                
for
future
in
concurrent
.
futures
.
as_completed
(
futures
)
:
                    
ret_val
=
future
.
result
(
)
                    
if
ret_val
!
=
self
.
TOOLS_SUCCESS
:
                        
return
ret_val
            
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
"
SUCCESS
:
infer
all
tests
passed
.
"
)
        
else
:
            
self
.
log
(
logging
.
WARNING
'
static
-
analysis
'
{
}
                     
"
Skipping
infer
autotest
because
it
is
only
available
on
linux64
!
"
)
        
return
self
.
TOOLS_SUCCESS
    
def
_verify_infer_checker
(
self
item
)
:
        
'
'
'
Given
a
checker
this
method
verifies
the
following
:
          
1
.
if
there
is
a
checker
.
json
and
checker
.
java
file
in
             
tools
/
infer
/
test
/
autotest
/
src
          
2
.
if
running
infer
on
checker
.
java
yields
the
same
result
as
checker
.
json
        
An
item
is
simply
a
dictionary
which
needs
to
have
a
name
field
set
which
is
the
        
name
of
the
checker
.
        
'
'
'
        
def
to_camelcase
(
str
)
:
            
return
'
'
.
join
(
[
s
.
capitalize
(
)
for
s
in
str
.
split
(
'
-
'
)
]
)
        
check
=
item
[
'
name
'
]
        
test_file_path
=
mozpath
.
join
(
self
.
__infer_tool
'
test
'
'
autotest
'
'
src
'
                                      
'
main
'
'
java
'
to_camelcase
(
check
)
)
        
test_file_path_java
=
test_file_path
+
'
.
java
'
        
test_file_path_json
=
test_file_path
+
'
.
json
'
        
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
"
RUNNING
:
infer
check
{
}
.
"
.
format
(
check
)
)
        
#
Verify
if
the
test
file
exists
for
this
checker
        
if
not
os
.
path
.
exists
(
test_file_path_java
)
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
"
ERROR
:
infer
check
{
}
doesn
'
t
have
a
test
file
.
"
.
format
(
check
)
)
            
return
self
.
TOOLS_CHECKER_NO_TEST_FILE
        
#
run
infer
on
a
particular
test
file
        
out_folder
=
mozpath
.
join
(
self
.
__infer_test_folder
'
test
-
infer
-
{
}
'
.
format
(
check
)
)
        
if
check
=
=
'
checkers
'
:
            
check_arg
=
[
'
-
a
'
'
checkers
'
]
        
else
:
            
check_arg
=
[
'
-
-
{
}
-
only
'
.
format
(
check
)
]
        
infer_args
=
[
self
.
_infer_path
'
run
'
]
+
check_arg
+
[
'
-
o
'
out_folder
'
-
-
'
]
        
gradle_args
=
[
'
autotest
:
compileInferTest
{
}
'
.
format
(
to_camelcase
(
check
)
)
]
        
rc
=
self
.
_gradle
(
gradle_args
infer_args
=
infer_args
autotest
=
True
)
        
if
rc
!
=
0
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
"
ERROR
:
infer
failed
to
execute
gradle
{
}
.
"
.
format
(
gradle_args
)
)
            
return
self
.
TOOLS_GRADLE_FAILED
        
issues
=
json
.
load
(
open
(
mozpath
.
join
(
out_folder
'
report
.
json
'
)
)
)
        
#
remove
folder
that
infer
creates
because
the
issues
are
loaded
into
memory
        
shutil
.
rmtree
(
out_folder
)
        
#
Verify
to
see
if
we
got
any
issues
if
not
raise
exception
        
if
not
issues
:
            
self
.
log
(
                
logging
.
ERROR
'
static
-
analysis
'
{
}
                
"
ERROR
:
infer
check
{
0
}
did
not
find
any
issues
in
its
associated
test
suite
.
"
                
.
format
(
check
)
            
)
            
return
self
.
TOOLS_CHECKER_RETURNED_NO_ISSUES
        
if
self
.
_dump_results
:
            
self
.
_build_autotest_result
(
test_file_path_json
issues
)
        
else
:
            
if
not
os
.
path
.
exists
(
test_file_path_json
)
:
                
#
Result
file
for
test
not
found
maybe
regenerate
it
?
                
self
.
log
(
                    
logging
.
ERROR
'
static
-
analysis
'
{
}
                    
"
ERROR
:
infer
result
file
not
found
for
check
{
0
}
"
.
format
(
check
)
                
)
                
return
self
.
TOOLS_CHECKER_RESULT_FILE_NOT_FOUND
            
#
Read
the
pre
-
determined
issues
            
baseline_issues
=
self
.
_get_autotest_stored_issues
(
test_file_path_json
)
            
def
ordered
(
obj
)
:
                
if
isinstance
(
obj
dict
)
:
                    
return
sorted
(
(
k
ordered
(
v
)
)
for
k
v
in
obj
.
items
(
)
)
                
if
isinstance
(
obj
list
)
:
                    
return
sorted
(
ordered
(
x
)
for
x
in
obj
)
                
return
obj
            
#
Compare
the
two
lists
            
if
ordered
(
issues
)
!
=
ordered
(
baseline_issues
)
:
                
error_str
=
"
ERROR
:
in
check
{
}
Expected
:
"
.
format
(
check
)
                
error_str
+
=
'
\
n
'
+
json
.
dumps
(
baseline_issues
indent
=
2
)
                
error_str
+
=
'
\
n
Got
:
\
n
'
+
json
.
dumps
(
issues
indent
=
2
)
                
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                         
'
ERROR
:
infer
autotest
for
check
{
}
failed
check
stdout
for
more
details
'
                         
.
format
(
check
)
)
                
print
(
error_str
)
                
return
self
.
TOOLS_CHECKER_DIFF_FAILED
        
return
self
.
TOOLS_SUCCESS
    
StaticAnalysisSubCommand
(
'
static
-
analysis
'
'
install
'
                              
'
Install
the
static
analysis
helper
tool
'
)
    
CommandArgument
(
'
source
'
nargs
=
'
?
'
type
=
str
                     
help
=
'
Where
to
fetch
a
local
archive
containing
the
static
-
analysis
and
'
                     
'
format
helper
tool
.
'
                          
'
It
will
be
installed
in
~
/
.
mozbuild
/
clang
-
tools
and
~
/
.
mozbuild
/
infer
.
'
                          
'
Can
be
omitted
in
which
case
the
latest
clang
-
tools
and
infer
'
                          
'
helper
for
the
platform
would
be
automatically
detected
and
installed
.
'
)
    
CommandArgument
(
'
-
-
skip
-
cache
'
action
=
'
store_true
'
                     
help
=
'
Skip
all
local
caches
to
force
re
-
fetching
the
helper
tool
.
'
                     
default
=
False
)
    
CommandArgument
(
'
-
-
force
'
action
=
'
store_true
'
                     
help
=
'
Force
re
-
install
even
though
the
tool
exists
in
mozbuild
.
'
                     
default
=
False
)
    
CommandArgument
(
'
-
-
minimal
-
install
'
action
=
'
store_true
'
                     
help
=
'
Download
only
clang
based
tool
.
'
                     
default
=
False
)
    
def
install
(
self
source
=
None
skip_cache
=
False
force
=
False
minimal_install
=
False
                
verbose
=
False
)
:
        
self
.
_set_log_level
(
verbose
)
        
rc
=
self
.
_get_clang_tools
(
force
=
force
skip_cache
=
skip_cache
                                   
source
=
source
verbose
=
verbose
)
        
if
rc
=
=
0
and
not
minimal_install
:
            
#
XXX
ignore
the
return
code
because
if
it
fails
or
not
infer
is
            
#
not
mandatory
but
clang
-
tidy
is
            
self
.
_get_infer
(
force
=
force
skip_cache
=
skip_cache
verbose
=
verbose
)
        
return
rc
    
StaticAnalysisSubCommand
(
'
static
-
analysis
'
'
clear
-
cache
'
                              
'
Delete
local
helpers
and
reset
static
analysis
helper
tool
cache
'
)
    
def
clear_cache
(
self
verbose
=
False
)
:
        
self
.
_set_log_level
(
verbose
)
        
rc
=
self
.
_get_clang_tools
(
force
=
True
download_if_needed
=
True
skip_cache
=
True
                                   
verbose
=
verbose
)
        
if
rc
=
=
0
:
            
self
.
_get_infer
(
force
=
True
download_if_needed
=
True
skip_cache
=
True
                            
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
return
rc
        
return
self
.
_artifact_manager
.
artifact_clear_cache
(
)
    
StaticAnalysisSubCommand
(
'
static
-
analysis
'
'
print
-
checks
'
                              
'
Print
a
list
of
the
static
analysis
checks
performed
by
default
'
)
    
def
print_checks
(
self
verbose
=
False
)
:
        
self
.
_set_log_level
(
verbose
)
        
rc
=
self
.
_get_clang_tools
(
verbose
=
verbose
)
        
if
rc
=
=
0
:
            
rc
=
self
.
_get_infer
(
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
return
rc
        
args
=
[
self
.
_clang_tidy_path
'
-
list
-
checks
'
'
-
checks
=
%
s
'
%
self
.
_get_checks
(
)
]
        
rc
=
self
.
_run_command_in_objdir
(
args
=
args
pass_thru
=
True
)
        
if
rc
!
=
0
:
            
return
rc
        
checkers
_
=
self
.
_get_infer_config
(
)
        
print
(
'
Infer
checks
:
'
)
        
for
checker
in
checkers
:
            
print
(
'
'
*
4
+
checker
)
        
return
0
    
Command
(
'
clang
-
format
'
category
=
'
misc
'
description
=
'
Run
clang
-
format
on
current
changes
'
)
    
CommandArgument
(
'
-
-
show
'
'
-
s
'
action
=
'
store_const
'
const
=
'
stdout
'
dest
=
'
output_path
'
                     
help
=
'
Show
diff
output
on
stdout
instead
of
applying
changes
'
)
    
CommandArgument
(
'
-
-
assume
-
filename
'
'
-
a
'
nargs
=
1
default
=
None
                     
help
=
'
This
option
is
usually
used
in
the
context
of
hg
-
formatsource
.
'
                          
'
When
reading
from
stdin
clang
-
format
assumes
this
'
                          
'
filename
to
look
for
a
style
config
file
(
with
'
                          
'
-
style
=
file
)
and
to
determine
the
language
.
When
'
                          
'
specifying
this
option
only
one
file
should
be
used
'
                          
'
as
an
input
and
the
output
will
be
forwarded
to
stdin
.
'
                          
'
This
option
also
impairs
the
download
of
the
clang
-
tools
'
                          
'
and
assumes
the
package
is
already
located
in
it
\
'
s
default
'
                          
'
location
'
)
    
CommandArgument
(
'
-
-
path
'
'
-
p
'
nargs
=
'
+
'
default
=
None
                     
help
=
'
Specify
the
path
(
s
)
to
reformat
'
)
    
CommandArgument
(
'
-
-
commit
'
'
-
c
'
default
=
None
                     
help
=
'
Specify
a
commit
to
reformat
from
.
'
                          
'
For
git
you
can
also
pass
a
range
of
commits
(
foo
.
.
bar
)
'
                          
'
to
format
all
of
them
at
the
same
time
.
'
)
    
CommandArgument
(
'
-
-
output
'
'
-
o
'
default
=
None
dest
=
'
output_path
'
                     
help
=
'
Specify
a
file
handle
to
write
clang
-
format
raw
output
instead
of
'
                          
'
applying
changes
.
This
can
be
stdout
or
a
file
path
.
'
)
    
CommandArgument
(
'
-
-
format
'
'
-
f
'
choices
=
(
'
diff
'
'
json
'
)
default
=
'
diff
'
                     
dest
=
'
output_format
'
                     
help
=
'
Specify
the
output
format
used
:
diff
is
the
raw
patch
provided
by
'
                     
'
clang
-
format
json
is
a
list
of
atomic
changes
to
process
.
'
)
    
CommandArgument
(
'
-
-
outgoing
'
default
=
False
action
=
'
store_true
'
                     
help
=
'
Run
clang
-
format
on
outgoing
files
from
mercurial
repository
'
)
    
def
clang_format
(
self
assume_filename
path
commit
output_path
=
None
output_format
=
'
diff
'
                     
verbose
=
False
outgoing
=
False
)
:
        
#
Run
clang
-
format
or
clang
-
format
-
diff
on
the
local
changes
        
#
or
files
/
directories
        
if
path
is
None
and
outgoing
:
            
repo
=
get_repository_object
(
self
.
topsrcdir
)
            
path
=
repo
.
get_outgoing_files
(
)
        
if
path
:
            
#
Create
the
full
path
list
            
def
path_maker
(
f_name
)
:
return
os
.
path
.
join
(
self
.
topsrcdir
f_name
)
            
path
=
map
(
path_maker
path
)
        
os
.
chdir
(
self
.
topsrcdir
)
        
#
Load
output
file
handle
either
stdout
or
a
file
handle
in
write
mode
        
output
=
None
        
if
output_path
is
not
None
:
            
output
=
sys
.
stdout
if
output_path
=
=
'
stdout
'
else
open
(
output_path
'
w
'
)
        
#
With
assume_filename
we
want
to
have
stdout
clean
since
the
result
of
the
        
#
format
will
be
redirected
to
stdout
.
Only
in
case
of
errror
we
        
#
write
something
to
stdout
.
        
#
We
don
'
t
actually
want
to
get
the
clang
-
tools
here
since
we
want
in
some
        
#
scenarios
to
do
this
in
parallel
so
we
relay
on
the
fact
that
the
tools
        
#
have
already
been
downloaded
via
'
.
/
mach
bootstrap
'
or
directly
via
        
#
'
.
/
mach
static
-
analysis
install
'
        
if
assume_filename
:
            
rc
=
self
.
_set_clang_tools_paths
(
)
            
if
rc
!
=
0
:
                
print
(
"
clang
-
format
:
Unable
to
set
path
to
clang
-
format
tools
.
"
)
                
return
rc
            
if
not
self
.
_do_clang_tools_exist
(
)
:
                
print
(
"
clang
-
format
:
Unable
to
set
locate
clang
-
format
tools
.
"
)
                
return
1
        
else
:
            
rc
=
self
.
_get_clang_tools
(
verbose
=
verbose
)
            
if
rc
!
=
0
:
                
return
rc
        
if
self
.
_is_version_eligible
(
)
is
False
:
            
self
.
log
(
logging
.
ERROR
'
static
-
analysis
'
{
}
                     
"
You
'
re
using
an
old
version
of
clang
-
format
binary
.
"
                     
"
Please
update
to
a
more
recent
one
by
running
:
'
.
/
mach
bootstrap
'
"
)
            
return
1
        
if
path
is
None
:
            
return
self
.
_run_clang_format_diff
(
self
.
_clang_format_diff
                                               
self
.
_clang_format_path
commit
output
)
        
if
assume_filename
:
            
return
self
.
_run_clang_format_in_console
(
self
.
_clang_format_path
                                                     
path
assume_filename
)
        
return
self
.
_run_clang_format_path
(
self
.
_clang_format_path
path
output
output_format
)
    
def
_verify_checker
(
self
item
checkers_results
)
:
        
check
=
item
[
'
name
'
]
        
test_file_path
=
mozpath
.
join
(
self
.
_clang_tidy_base_path
"
test
"
check
)
        
test_file_path_cpp
=
test_file_path
+
'
.
cpp
'
        
test_file_path_json
=
test_file_path
+
'
.
json
'
        
self
.
log
(
logging
.
INFO
'
static
-
analysis
'
{
}
                 
"
RUNNING
:
clang
-
tidy
checker
{
}
.
"
.
format
(
check
)
)
        
#
Structured
information
in
case
a
checker
fails
        
checker_error
=
{
            
'
checker
-
name
'
:
check
            
'
checker
-
error
'
:
'
'
            
'
info1
'
:
'
'
            
'
info2
'
:
'
'
            
'
info3
'
:
'
'
        
}
        
#
Verify
if
this
checker
actually
exists
        
if
check
not
in
self
.
_clang_tidy_checks
:
            
checker_error
[
'
checker
-
error
'
]
=
self
.
TOOLS_CHECKER_NOT_FOUND
            
checkers_results
.
append
(
checker_error
)
            
return
self
.
TOOLS_CHECKER_NOT_FOUND
        
#
Verify
if
the
test
file
exists
for
this
checker
        
if
not
os
.
path
.
exists
(
test_file_path_cpp
)
:
            
checker_error
[
'
checker
-
error
'
]
=
self
.
TOOLS_CHECKER_NO_TEST_FILE
            
checkers_results
.
append
(
checker_error
)
            
return
self
.
TOOLS_CHECKER_NO_TEST_FILE
        
issues
clang_output
=
self
.
_run_analysis
(
            
checks
=
'
-
*
'
+
check
header_filter
=
'
'
sources
=
[
test_file_path_cpp
]
)
        
if
issues
is
None
:
            
return
self
.
TOOLS_CHECKER_FAILED_FILE
        
#
Verify
to
see
if
we
got
any
issues
if
not
raise
exception
        
if
not
issues
:
            
checker_error
[
'
checker
-
error
'
]
=
self
.
TOOLS_CHECKER_RETURNED_NO_ISSUES
            
checker_error
[
'
info1
'
]
=
clang_output
            
checkers_results
.
append
(
checker_error
)
            
return
self
.
TOOLS_CHECKER_RETURNED_NO_ISSUES
        
#
Also
store
the
'
reliability
'
index
for
this
checker
        
issues
.
append
(
{
'
reliability
'
:
item
[
'
reliability
'
]
}
)
        
if
self
.
_dump_results
:
            
self
.
_build_autotest_result
(
test_file_path_json
json
.
dumps
(
issues
)
)
        
else
:
            
if
not
os
.
path
.
exists
(
test_file_path_json
)
:
                
#
Result
file
for
test
not
found
maybe
regenerate
it
?
                
checker_error
[
'
checker
-
error
'
]
=
self
.
TOOLS_CHECKER_RESULT_FILE_NOT_FOUND
                
checkers_results
.
append
(
checker_error
)
                
return
self
.
TOOLS_CHECKER_RESULT_FILE_NOT_FOUND
            
#
Read
the
pre
-
determined
issues
            
baseline_issues
=
self
.
_get_autotest_stored_issues
(
test_file_path_json
)
            
#
Compare
the
two
lists
            
if
issues
!
=
baseline_issues
:
                
checker_error
[
'
checker
-
error
'
]
=
self
.
TOOLS_CHECKER_DIFF_FAILED
                
checker_error
[
'
info1
'
]
=
baseline_issues
                
checker_error
[
'
info2
'
]
=
issues
                
checker_error
[
'
info3
'
]
=
clang_output
                
checkers_results
.
append
(
checker_error
)
                
return
self
.
TOOLS_CHECKER_DIFF_FAILED
        
return
self
.
TOOLS_SUCCESS
    
def
_build_autotest_result
(
self
file
issues
)
:
        
with
open
(
file
'
w
'
)
as
f
:
            
f
.
write
(
issues
)
    
def
_get_autotest_stored_issues
(
self
file
)
:
        
with
open
(
file
)
as
f
:
            
return
json
.
load
(
f
)
    
def
_parse_issues
(
self
clang_output
)
:
        
'
'
'
        
Parse
clang
-
tidy
output
into
structured
issues
        
'
'
'
        
#
Limit
clang
output
parsing
to
'
Enabled
checks
:
'
        
end
=
re
.
search
(
r
'
^
Enabled
checks
:
\
n
'
clang_output
re
.
MULTILINE
)
        
if
end
is
not
None
:
            
clang_output
=
clang_output
[
:
end
.
start
(
)
-
1
]
        
platform
_
=
self
.
platform
        
#
Starting
with
clang
8
for
the
diagnostic
messages
we
have
multiple
LF
CR
        
#
in
order
to
be
compatiable
with
msvc
compiler
format
and
for
this
        
#
we
are
not
interested
to
match
the
end
of
line
.
        
regex_string
=
r
'
(
.
+
)
:
(
\
d
+
)
:
(
\
d
+
)
:
(
warning
|
error
)
:
(
[
^
\
[
\
]
\
n
]
+
)
(
?
:
\
[
(
[
\
.
\
w
-
]
+
)
\
]
)
'
        
#
For
non
'
win
'
based
platforms
we
also
need
the
'
end
of
the
line
'
regex
        
if
platform
not
in
(
'
win64
'
'
win32
'
)
:
            
regex_string
+
=
'
?
'
        
regex_header
=
re
.
compile
(
regex_string
re
.
MULTILINE
)
        
#
Sort
headers
by
positions
        
headers
=
sorted
(
            
regex_header
.
finditer
(
clang_output
)
            
key
=
lambda
h
:
h
.
start
(
)
        
)
        
issues
=
[
]
        
for
_
header
in
enumerate
(
headers
)
:
            
header_group
=
header
.
groups
(
)
            
element
=
[
header_group
[
3
]
header_group
[
4
]
header_group
[
5
]
]
            
issues
.
append
(
element
)
        
return
issues
    
def
_get_checks
(
self
)
:
        
checks
=
'
-
*
'
        
try
:
            
config
=
self
.
_clang_tidy_config
            
for
item
in
config
[
'
clang_checkers
'
]
:
                
if
item
.
get
(
'
publish
'
True
)
:
                    
checks
+
=
'
'
+
item
[
'
name
'
]
        
except
Exception
:
            
print
(
'
Looks
like
config
.
yaml
is
not
valid
so
we
are
unable
to
'
                  
'
determine
default
checkers
using
\
'
-
checks
=
-
*
mozilla
-
*
\
'
'
)
            
checks
+
=
'
mozilla
-
*
'
        
finally
:
            
return
checks
    
def
_get_checks_config
(
self
)
:
        
config_list
=
[
]
        
checker_config
=
{
}
        
try
:
            
config
=
self
.
_clang_tidy_config
            
for
checker
in
config
[
'
clang_checkers
'
]
:
                
if
checker
.
get
(
'
publish
'
True
)
and
'
config
'
in
checker
:
                    
for
checker_option
in
checker
[
'
config
'
]
:
                        
#
Verify
if
the
format
of
the
Option
is
correct
                        
#
possibilities
are
:
                        
#
1
.
CheckerName
.
Option
                        
#
2
.
Option
-
>
that
will
become
CheckerName
.
Option
                        
if
not
checker_option
[
'
key
'
]
.
startswith
(
checker
[
'
name
'
]
)
:
                            
checker_option
[
'
key
'
]
=
"
{
}
.
{
}
"
.
format
(
                                
checker
[
'
name
'
]
checker_option
[
'
key
'
]
)
                    
config_list
+
=
checker
[
'
config
'
]
            
checker_config
[
'
CheckOptions
'
]
=
config_list
        
except
Exception
:
            
print
(
'
Looks
like
config
.
yaml
is
not
valid
so
we
are
unable
to
'
                  
'
determine
configuration
for
checkers
so
using
default
'
)
            
checker_config
=
None
        
finally
:
            
return
checker_config
    
def
_get_config_environment
(
self
)
:
        
ran_configure
=
False
        
config
=
None
        
builder
=
Build
(
self
.
_mach_context
)
        
try
:
            
config
=
self
.
config_environment
        
except
Exception
:
            
print
(
'
Looks
like
configure
has
not
run
yet
running
it
now
.
.
.
'
)
            
rc
=
builder
.
configure
(
)
            
if
rc
!
=
0
:
                
return
(
rc
config
ran_configure
)
            
ran_configure
=
True
            
try
:
                
config
=
self
.
config_environment
            
except
Exception
:
                
pass
        
return
(
0
config
ran_configure
)
    
def
_build_compile_db
(
self
verbose
=
False
)
:
        
self
.
_compile_db
=
mozpath
.
join
(
self
.
topobjdir
'
compile_commands
.
json
'
)
        
if
os
.
path
.
exists
(
self
.
_compile_db
)
:
            
return
0
        
rc
config
ran_configure
=
self
.
_get_config_environment
(
)
        
if
rc
!
=
0
:
            
return
rc
        
if
ran_configure
:
            
#
Configure
may
have
created
the
compilation
database
if
the
            
#
mozconfig
enables
building
the
CompileDB
backend
by
default
            
#
So
we
recurse
to
see
if
the
file
exists
once
again
.
            
return
self
.
_build_compile_db
(
verbose
=
verbose
)
        
if
config
:
            
print
(
'
Looks
like
a
clang
compilation
database
has
not
been
'
                  
'
created
yet
creating
it
now
.
.
.
'
)
            
builder
=
Build
(
self
.
_mach_context
)
            
rc
=
builder
.
build_backend
(
[
'
CompileDB
'
]
verbose
=
verbose
)
            
if
rc
!
=
0
:
                
return
rc
            
assert
os
.
path
.
exists
(
self
.
_compile_db
)
            
return
0
    
def
_build_export
(
self
jobs
verbose
=
False
)
:
        
def
on_line
(
line
)
:
            
self
.
log
(
logging
.
INFO
'
build_output
'
{
'
line
'
:
line
}
'
{
line
}
'
)
        
builder
=
Build
(
self
.
_mach_context
)
        
#
First
install
what
we
can
through
install
manifests
.
        
rc
=
builder
.
_run_make
(
directory
=
self
.
topobjdir
target
=
'
pre
-
export
'
                               
line_handler
=
None
silent
=
not
verbose
)
        
if
rc
!
=
0
:
            
return
rc
        
#
Then
build
the
rest
of
the
build
dependencies
by
running
the
full
        
#
export
target
because
we
can
'
t
do
anything
better
.
        
return
builder
.
_run_make
(
directory
=
self
.
topobjdir
target
=
'
export
'
                                 
line_handler
=
None
silent
=
not
verbose
                                 
num_jobs
=
jobs
)
    
def
_set_clang_tools_paths
(
self
)
:
        
rc
config
_
=
self
.
_get_config_environment
(
)
        
if
rc
!
=
0
:
            
return
rc
        
self
.
_clang_tools_path
=
mozpath
.
join
(
self
.
_mach_context
.
state_dir
"
clang
-
tools
"
)
        
self
.
_clang_tidy_path
=
mozpath
.
join
(
self
.
_clang_tools_path
"
clang
-
tidy
"
"
bin
"
                                             
"
clang
-
tidy
"
+
config
.
substs
.
get
(
'
BIN_SUFFIX
'
'
'
)
)
        
self
.
_clang_format_path
=
mozpath
.
join
(
            
self
.
_clang_tools_path
"
clang
-
tidy
"
"
bin
"
            
"
clang
-
format
"
+
config
.
substs
.
get
(
'
BIN_SUFFIX
'
'
'
)
)
        
self
.
_clang_apply_replacements
=
mozpath
.
join
(
            
self
.
_clang_tools_path
"
clang
-
tidy
"
"
bin
"
            
"
clang
-
apply
-
replacements
"
+
config
.
substs
.
get
(
'
BIN_SUFFIX
'
'
'
)
)
        
self
.
_run_clang_tidy_path
=
mozpath
.
join
(
self
.
_clang_tools_path
"
clang
-
tidy
"
                                                 
"
share
"
"
clang
"
"
run
-
clang
-
tidy
.
py
"
)
        
self
.
_clang_format_diff
=
mozpath
.
join
(
self
.
_clang_tools_path
"
clang
-
tidy
"
                                               
"
share
"
"
clang
"
"
clang
-
format
-
diff
.
py
"
)
        
return
0
    
def
_do_clang_tools_exist
(
self
)
:
        
return
os
.
path
.
exists
(
self
.
_clang_tidy_path
)
and
\
               
os
.
path
.
exists
(
self
.
_clang_format_path
)
and
\
               
os
.
path
.
exists
(
self
.
_clang_apply_replacements
)
and
\
               
os
.
path
.
exists
(
self
.
_run_clang_tidy_path
)
    
def
_get_clang_tools
(
self
force
=
False
skip_cache
=
False
                         
source
=
None
download_if_needed
=
True
                         
verbose
=
False
)
:
        
rc
=
self
.
_set_clang_tools_paths
(
)
        
if
rc
!
=
0
:
            
return
rc
        
if
self
.
_do_clang_tools_exist
(
)
and
not
force
:
            
return
0
        
if
os
.
path
.
isdir
(
self
.
_clang_tools_path
)
and
download_if_needed
:
            
#
The
directory
exists
perhaps
it
'
s
corrupted
?
Delete
it
            
#
and
start
from
scratch
.
            
shutil
.
rmtree
(
self
.
_clang_tools_path
)
            
return
self
.
_get_clang_tools
(
force
=
force
skip_cache
=
skip_cache
                                         
source
=
source
verbose
=
verbose
                                         
download_if_needed
=
download_if_needed
)
        
#
Create
base
directory
where
we
store
clang
binary
        
os
.
mkdir
(
self
.
_clang_tools_path
)
        
if
source
:
            
return
self
.
_get_clang_tools_from_source
(
source
)
        
self
.
_artifact_manager
=
PackageFrontend
(
self
.
_mach_context
)
        
if
not
download_if_needed
:
            
return
0
        
job
_
=
self
.
platform
        
if
job
is
None
:
            
raise
Exception
(
'
The
current
platform
isn
\
'
t
supported
.
'
                            
'
Currently
only
the
following
platforms
are
'
                            
'
supported
:
win32
/
win64
linux64
and
macosx64
.
'
)
        
job
+
=
'
-
clang
-
tidy
'
        
#
We
want
to
unpack
data
in
the
clang
-
tidy
mozbuild
folder
        
currentWorkingDir
=
os
.
getcwd
(
)
        
os
.
chdir
(
self
.
_clang_tools_path
)
        
rc
=
self
.
_artifact_manager
.
artifact_toolchain
(
verbose
=
verbose
                                                       
skip_cache
=
skip_cache
                                                       
from_build
=
[
job
]
                                                       
no_unpack
=
False
                                                       
retry
=
0
)
        
#
Change
back
the
cwd
        
os
.
chdir
(
currentWorkingDir
)
        
return
rc
    
def
_get_clang_tools_from_source
(
self
filename
)
:
        
from
mozbuild
.
action
.
tooltool
import
unpack_file
        
clang_tidy_path
=
mozpath
.
join
(
self
.
_mach_context
.
state_dir
                                       
"
clang
-
tools
"
)
        
currentWorkingDir
=
os
.
getcwd
(
)
        
os
.
chdir
(
clang_tidy_path
)
        
unpack_file
(
filename
)
        
#
Change
back
the
cwd
        
os
.
chdir
(
currentWorkingDir
)
        
clang_path
=
mozpath
.
join
(
clang_tidy_path
'
clang
'
)
        
if
not
os
.
path
.
isdir
(
clang_path
)
:
            
raise
Exception
(
'
Extracted
the
archive
but
didn
\
'
t
find
'
                            
'
the
expected
output
'
)
        
assert
os
.
path
.
exists
(
self
.
_clang_tidy_path
)
        
assert
os
.
path
.
exists
(
self
.
_clang_format_path
)
        
assert
os
.
path
.
exists
(
self
.
_clang_apply_replacements
)
        
assert
os
.
path
.
exists
(
self
.
_run_clang_tidy_path
)
        
return
0
    
def
_get_clang_format_diff_command
(
self
commit
)
:
        
if
self
.
repository
.
name
=
=
'
hg
'
:
            
args
=
[
"
hg
"
"
diff
"
"
-
U0
"
]
            
if
commit
:
                
args
+
=
[
"
-
c
"
commit
]
            
else
:
                
args
+
=
[
"
-
r
"
"
.
^
"
]
            
for
dot_extension
in
self
.
_format_include_extensions
:
                
args
+
=
[
'
-
-
include
'
'
glob
:
*
*
{
0
}
'
.
format
(
dot_extension
)
]
            
args
+
=
[
'
-
-
exclude
'
'
listfile
:
{
0
}
'
.
format
(
self
.
_format_ignore_file
)
]
        
else
:
            
commit_range
=
"
HEAD
"
#
All
uncommitted
changes
.
            
if
commit
:
                
commit_range
=
commit
if
"
.
.
"
in
commit
else
"
{
}
~
.
.
{
}
"
.
format
(
commit
commit
)
            
args
=
[
"
git
"
"
diff
"
"
-
-
no
-
color
"
"
-
U0
"
commit_range
"
-
-
"
]
            
for
dot_extension
in
self
.
_format_include_extensions
:
                
args
+
=
[
'
*
{
0
}
'
.
format
(
dot_extension
)
]
            
#
git
-
diff
doesn
'
t
support
an
'
exclude
-
from
-
files
'
param
but
            
#
allow
to
add
individual
exclude
pattern
since
v1
.
9
see
            
#
https
:
/
/
git
-
scm
.
com
/
docs
/
gitglossary
#
gitglossary
-
aiddefpathspecapathspec
            
with
open
(
self
.
_format_ignore_file
'
rb
'
)
as
exclude_pattern_file
:
                
for
pattern
in
exclude_pattern_file
.
readlines
(
)
:
                    
pattern
=
pattern
.
rstrip
(
)
                    
pattern
=
pattern
.
replace
(
'
.
*
'
'
*
*
'
)
                    
if
not
pattern
or
pattern
.
startswith
(
'
#
'
)
:
                        
continue
#
empty
or
comment
                    
magics
=
[
'
exclude
'
]
                    
if
pattern
.
startswith
(
'
^
'
)
:
                        
magics
+
=
[
'
top
'
]
                        
pattern
=
pattern
[
1
:
]
                    
args
+
=
[
'
:
(
{
0
}
)
{
1
}
'
.
format
(
'
'
.
join
(
magics
)
pattern
)
]
        
return
args
    
def
_get_infer
(
self
force
=
False
skip_cache
=
False
download_if_needed
=
True
                   
verbose
=
False
intree_tool
=
False
)
:
        
rc
config
_
=
self
.
_get_config_environment
(
)
        
if
rc
!
=
0
:
            
return
rc
        
infer_path
=
self
.
topsrcdir
if
intree_tool
else
\
            
mozpath
.
join
(
self
.
_mach_context
.
state_dir
'
infer
'
)
        
self
.
_infer_path
=
mozpath
.
join
(
infer_path
'
infer
'
'
bin
'
'
infer
'
+
                                        
config
.
substs
.
get
(
'
BIN_SUFFIX
'
'
'
)
)
        
if
intree_tool
:
            
return
not
os
.
path
.
exists
(
self
.
_infer_path
)
        
if
os
.
path
.
exists
(
self
.
_infer_path
)
and
not
force
:
            
return
0
        
if
os
.
path
.
isdir
(
infer_path
)
and
download_if_needed
:
            
#
The
directory
exists
perhaps
it
'
s
corrupted
?
Delete
it
            
#
and
start
from
scratch
.
            
shutil
.
rmtree
(
infer_path
)
            
return
self
.
_get_infer
(
force
=
force
skip_cache
=
skip_cache
                                   
verbose
=
verbose
                                   
download_if_needed
=
download_if_needed
)
        
os
.
mkdir
(
infer_path
)
        
self
.
_artifact_manager
=
PackageFrontend
(
self
.
_mach_context
)
        
if
not
download_if_needed
:
            
return
0
        
job
_
=
self
.
platform
        
if
job
!
=
'
linux64
'
:
            
return
-
1
        
else
:
            
job
+
=
'
-
infer
'
        
#
We
want
to
unpack
data
in
the
infer
mozbuild
folder
        
currentWorkingDir
=
os
.
getcwd
(
)
        
os
.
chdir
(
infer_path
)
        
rc
=
self
.
_artifact_manager
.
artifact_toolchain
(
verbose
=
verbose
                                                       
skip_cache
=
skip_cache
                                                       
from_build
=
[
job
]
                                                       
no_unpack
=
False
                                                       
retry
=
0
)
        
#
Change
back
the
cwd
        
os
.
chdir
(
currentWorkingDir
)
        
return
rc
    
def
_run_clang_format_diff
(
self
clang_format_diff
clang_format
commit
output_file
)
:
        
#
Run
clang
-
format
on
the
diff
        
#
Note
that
this
will
potentially
miss
a
lot
things
        
from
subprocess
import
Popen
PIPE
check_output
CalledProcessError
        
diff_process
=
Popen
(
self
.
_get_clang_format_diff_command
(
commit
)
stdout
=
PIPE
)
        
args
=
[
sys
.
executable
clang_format_diff
"
-
p1
"
"
-
binary
=
%
s
"
%
clang_format
]
        
if
not
output_file
:
            
args
.
append
(
"
-
i
"
)
        
try
:
            
output
=
check_output
(
args
stdin
=
diff_process
.
stdout
)
            
if
output_file
:
                
#
We
want
to
print
the
diffs
                
print
(
output
file
=
output_file
)
            
return
0
        
except
CalledProcessError
as
e
:
            
#
Something
wrong
happend
            
print
(
"
clang
-
format
:
An
error
occured
while
running
clang
-
format
-
diff
.
"
)
            
return
e
.
returncode
    
def
_is_ignored_path
(
self
ignored_dir_re
f
)
:
        
#
Remove
upto
topsrcdir
in
pathname
and
match
        
if
f
.
startswith
(
self
.
topsrcdir
+
'
/
'
)
:
            
match_f
=
f
[
len
(
self
.
topsrcdir
+
'
/
'
)
:
]
        
else
:
            
match_f
=
f
        
return
re
.
match
(
ignored_dir_re
match_f
)
    
def
_generate_path_list
(
self
paths
verbose
=
True
)
:
        
path_to_third_party
=
os
.
path
.
join
(
self
.
topsrcdir
self
.
_format_ignore_file
)
        
ignored_dir
=
[
]
        
with
open
(
path_to_third_party
'
r
'
)
as
fh
:
            
for
line
in
fh
:
                
#
Remove
comments
and
empty
lines
                
if
line
.
startswith
(
'
#
'
)
or
len
(
line
.
strip
(
)
)
=
=
0
:
                    
continue
                
#
The
regexp
is
to
make
sure
we
are
managing
relative
paths
                
ignored_dir
.
append
(
r
"
^
[
\
.
/
]
*
"
+
line
.
rstrip
(
)
)
        
#
Generates
the
list
of
regexp
        
ignored_dir_re
=
'
(
%
s
)
'
%
'
|
'
.
join
(
ignored_dir
)
        
extensions
=
self
.
_format_include_extensions
        
path_list
=
[
]
        
for
f
in
paths
:
            
if
self
.
_is_ignored_path
(
ignored_dir_re
f
)
:
                
#
Early
exit
if
we
have
provided
an
ignored
directory
                
if
verbose
:
                    
print
(
"
clang
-
format
:
Ignored
third
party
code
'
{
0
}
'
"
.
format
(
f
)
)
                
continue
            
if
os
.
path
.
isdir
(
f
)
:
                
#
Processing
a
directory
generate
the
file
list
                
for
folder
subs
files
in
os
.
walk
(
f
)
:
                    
subs
.
sort
(
)
                    
for
filename
in
sorted
(
files
)
:
                        
f_in_dir
=
os
.
path
.
join
(
folder
filename
)
                        
if
(
f_in_dir
.
endswith
(
extensions
)
                            
and
not
self
.
_is_ignored_path
(
ignored_dir_re
f_in_dir
)
)
:
                            
#
Supported
extension
and
accepted
path
                            
path_list
.
append
(
f_in_dir
)
            
else
:
                
#
Make
sure
that
the
file
exists
and
it
has
a
supported
extension
                
if
os
.
path
.
isfile
(
f
)
and
f
.
endswith
(
extensions
)
:
                    
path_list
.
append
(
f
)
        
return
path_list
    
def
_run_clang_format_in_console
(
self
clang_format
paths
assume_filename
)
:
        
path_list
=
self
.
_generate_path_list
(
assume_filename
False
)
        
if
path_list
=
=
[
]
:
            
return
0
        
#
We
use
-
assume
-
filename
in
order
to
better
determine
the
path
for
        
#
the
.
clang
-
format
when
it
is
ran
outside
of
the
repo
for
example
        
#
by
the
extension
hg
-
formatsource
        
args
=
[
clang_format
"
-
assume
-
filename
=
{
}
"
.
format
(
assume_filename
[
0
]
)
]
        
process
=
subprocess
.
Popen
(
args
stdin
=
subprocess
.
PIPE
)
        
with
open
(
paths
[
0
]
'
r
'
)
as
fin
:
            
process
.
stdin
.
write
(
fin
.
read
(
)
)
            
process
.
stdin
.
close
(
)
            
process
.
wait
(
)
            
return
process
.
returncode
    
def
_run_clang_format_path
(
self
clang_format
paths
output_file
output_format
)
:
        
#
Run
clang
-
format
on
files
or
directories
directly
        
from
subprocess
import
check_output
CalledProcessError
        
if
output_format
=
=
'
json
'
:
            
#
Get
replacements
in
xml
then
process
to
json
            
args
=
[
clang_format
'
-
output
-
replacements
-
xml
'
]
        
else
:
            
args
=
[
clang_format
'
-
i
'
]
        
if
output_file
:
            
#
We
just
want
to
show
the
diff
we
create
the
directory
to
copy
it
            
tmpdir
=
os
.
path
.
join
(
self
.
topobjdir
'
tmp
'
)
            
if
not
os
.
path
.
exists
(
tmpdir
)
:
                
os
.
makedirs
(
tmpdir
)
        
path_list
=
self
.
_generate_path_list
(
paths
)
        
if
path_list
=
=
[
]
:
            
return
        
print
(
"
Processing
%
d
file
(
s
)
.
.
.
"
%
len
(
path_list
)
)
        
if
output_file
:
            
patches
=
{
}
            
for
i
in
range
(
0
len
(
path_list
)
)
:
                
l
=
path_list
[
i
:
(
i
+
1
)
]
                
#
Copy
the
files
into
a
temp
directory
                
#
and
run
clang
-
format
on
the
temp
directory
                
#
and
show
the
diff
                
original_path
=
l
[
0
]
                
local_path
=
ntpath
.
basename
(
original_path
)
                
target_file
=
os
.
path
.
join
(
tmpdir
local_path
)
                
faketmpdir
=
os
.
path
.
dirname
(
target_file
)
                
if
not
os
.
path
.
isdir
(
faketmpdir
)
:
                    
os
.
makedirs
(
faketmpdir
)
                
shutil
.
copy
(
l
[
0
]
faketmpdir
)
                
l
[
0
]
=
target_file
                
#
Run
clang
-
format
on
the
list
                
try
:
                    
output
=
check_output
(
args
+
l
)
                    
if
output
and
output_format
=
=
'
json
'
:
                        
patches
[
original_path
]
=
self
.
_parse_xml_output
(
original_path
output
)
                
except
CalledProcessError
as
e
:
                    
#
Something
wrong
happend
                    
print
(
"
clang
-
format
:
An
error
occured
while
running
clang
-
format
.
"
)
                    
return
e
.
returncode
                
#
show
the
diff
                
if
output_format
=
=
'
diff
'
:
                    
diff_command
=
[
"
diff
"
"
-
u
"
original_path
target_file
]
                    
try
:
                        
output
=
check_output
(
diff_command
)
                    
except
CalledProcessError
as
e
:
                        
#
diff
-
u
returns
0
when
no
change
                        
#
here
we
expect
changes
.
if
we
are
here
this
means
that
                        
#
there
is
a
diff
to
show
                        
if
e
.
output
:
                            
#
Replace
the
temp
path
by
the
path
relative
to
the
repository
to
                            
#
display
a
valid
patch
                            
relative_path
=
os
.
path
.
relpath
(
original_path
self
.
topsrcdir
)
                            
patch
=
e
.
output
.
replace
(
target_file
relative_path
)
                            
patch
=
patch
.
replace
(
original_path
relative_path
)
                            
patches
[
original_path
]
=
patch
            
if
output_format
=
=
'
json
'
:
                
output
=
json
.
dumps
(
patches
indent
=
4
)
            
else
:
                
#
Display
all
the
patches
at
once
                
output
=
'
\
n
'
.
join
(
patches
.
values
(
)
)
            
#
Output
to
specified
file
or
stdout
            
print
(
output
file
=
output_file
)
            
shutil
.
rmtree
(
tmpdir
)
            
return
0
        
#
Run
clang
-
format
in
parallel
trying
to
saturate
all
of
the
available
cores
.
        
import
concurrent
.
futures
        
import
multiprocessing
        
import
math
        
max_workers
=
multiprocessing
.
cpu_count
(
)
        
#
To
maximize
CPU
usage
when
there
are
few
items
to
handle
        
#
underestimate
the
number
of
items
per
batch
then
dispatch
        
#
outstanding
items
across
workers
.
Per
definition
each
worker
will
        
#
handle
at
most
one
outstanding
item
.
        
batch_size
=
int
(
math
.
floor
(
float
(
len
(
path_list
)
)
/
max_workers
)
)
        
outstanding_items
=
len
(
path_list
)
-
batch_size
*
max_workers
        
batches
=
[
]
        
i
=
0
        
while
i
<
len
(
path_list
)
:
            
num_items
=
batch_size
+
(
1
if
outstanding_items
>
0
else
0
)
            
batches
.
append
(
args
+
path_list
[
i
:
(
i
+
num_items
)
]
)
            
outstanding_items
-
=
1
            
i
+
=
num_items
        
error_code
=
None
        
with
concurrent
.
futures
.
ThreadPoolExecutor
(
max_workers
=
max_workers
)
as
executor
:
            
futures
=
[
]
            
for
batch
in
batches
:
                
futures
.
append
(
executor
.
submit
(
run_one_clang_format_batch
batch
)
)
            
for
future
in
concurrent
.
futures
.
as_completed
(
futures
)
:
                
#
Wait
for
every
task
to
finish
                
ret_val
=
future
.
result
(
)
                
if
ret_val
is
not
None
:
                    
error_code
=
ret_val
            
if
error_code
is
not
None
:
                
return
error_code
        
return
0
    
def
_parse_xml_output
(
self
path
clang_output
)
:
        
'
'
'
        
Parse
the
clang
-
format
XML
output
to
convert
it
in
a
JSON
compatible
        
list
of
patches
and
calculates
line
level
informations
from
the
        
character
level
provided
changes
.
        
'
'
'
        
content
=
open
(
path
'
r
'
)
.
read
(
)
.
decode
(
'
utf
-
8
'
)
        
def
_nb_of_lines
(
start
end
)
:
            
return
len
(
content
[
start
:
end
]
.
splitlines
(
)
)
        
def
_build
(
replacement
)
:
            
offset
=
int
(
replacement
.
attrib
[
'
offset
'
]
)
            
length
=
int
(
replacement
.
attrib
[
'
length
'
]
)
            
last_line
=
content
.
rfind
(
'
\
n
'
0
offset
)
            
return
{
                
'
replacement
'
:
replacement
.
text
                
'
char_offset
'
:
offset
                
'
char_length
'
:
length
                
'
line
'
:
_nb_of_lines
(
0
offset
)
                
'
line_offset
'
:
last_line
!
=
-
1
and
(
offset
-
last_line
)
or
0
                
'
lines_modified
'
:
_nb_of_lines
(
offset
offset
+
length
)
            
}
        
return
[
            
_build
(
replacement
)
            
for
replacement
in
ET
.
fromstring
(
clang_output
)
.
findall
(
'
replacement
'
)
        
]
class
SymbolsAction
(
argparse
.
Action
)
:
    
def
__call__
(
self
parser
namespace
values
option_string
=
None
)
:
        
#
If
this
function
is
called
it
means
the
-
-
symbols
option
was
given
        
#
so
we
want
to
store
the
value
True
if
no
explicit
value
was
given
        
#
to
the
option
.
        
setattr
(
namespace
self
.
dest
values
or
True
)
CommandProvider
class
PackageFrontend
(
MachCommandBase
)
:
    
"
"
"
Fetch
and
install
binary
artifacts
from
Mozilla
automation
.
"
"
"
    
Command
(
        
"
artifact
"
        
category
=
"
post
-
build
"
        
description
=
"
Use
pre
-
built
artifacts
to
build
Firefox
.
"
    
)
    
def
artifact
(
self
)
:
        
"
"
"
Download
cache
and
install
pre
-
built
binary
artifacts
to
build
Firefox
.
        
Use
|
mach
build
|
as
normal
to
freshen
your
installed
binary
libraries
:
        
artifact
builds
automatically
download
cache
and
install
binary
        
artifacts
from
Mozilla
automation
replacing
whatever
may
be
in
your
        
object
directory
.
Use
|
mach
artifact
last
|
to
see
what
binary
artifacts
        
were
last
used
.
        
Never
build
libxul
again
!
        
"
"
"
        
pass
    
def
_make_artifacts
(
        
self
        
tree
=
None
        
job
=
None
        
skip_cache
=
False
        
download_tests
=
True
        
download_symbols
=
False
        
download_host_bins
=
False
    
)
:
        
state_dir
=
self
.
_mach_context
.
state_dir
        
cache_dir
=
os
.
path
.
join
(
state_dir
"
package
-
frontend
"
)
        
hg
=
None
        
if
conditions
.
is_hg
(
self
)
:
            
hg
=
self
.
substs
[
"
HG
"
]
        
git
=
None
        
if
conditions
.
is_git
(
self
)
:
            
git
=
self
.
substs
[
"
GIT
"
]
        
#
If
we
'
re
building
Thunderbird
we
should
be
checking
for
comm
-
central
artifacts
.
        
topsrcdir
=
self
.
substs
.
get
(
"
commtopsrcdir
"
self
.
topsrcdir
)
        
from
mozbuild
.
artifacts
import
Artifacts
        
artifacts
=
Artifacts
(
            
tree
            
self
.
substs
            
self
.
defines
            
job
            
log
=
self
.
log
            
cache_dir
=
cache_dir
            
skip_cache
=
skip_cache
            
hg
=
hg
            
git
=
git
            
topsrcdir
=
topsrcdir
            
download_tests
=
download_tests
            
download_symbols
=
download_symbols
            
download_host_bins
=
download_host_bins
        
)
        
return
artifacts
    
ArtifactSubCommand
(
"
artifact
"
"
install
"
"
Install
a
good
pre
-
built
artifact
.
"
)
    
CommandArgument
(
        
"
source
"
        
metavar
=
"
SRC
"
        
nargs
=
"
?
"
        
type
=
str
        
help
=
"
Where
to
fetch
and
install
artifacts
from
.
Can
be
omitted
in
"
        
"
which
case
the
current
hg
repository
is
inspected
;
an
hg
revision
;
"
        
"
a
remote
URL
;
or
a
local
file
.
"
        
default
=
None
    
)
    
CommandArgument
(
        
"
-
-
skip
-
cache
"
        
action
=
"
store_true
"
        
help
=
"
Skip
all
local
caches
to
force
re
-
fetching
remote
artifacts
.
"
        
default
=
False
    
)
    
CommandArgument
(
"
-
-
no
-
tests
"
action
=
"
store_true
"
help
=
"
Don
'
t
install
tests
.
"
)
    
CommandArgument
(
        
"
-
-
symbols
"
nargs
=
"
?
"
action
=
SymbolsAction
help
=
"
Download
symbols
.
"
    
)
    
CommandArgument
(
"
-
-
host
-
bins
"
action
=
"
store_true
"
help
=
"
Download
host
binaries
.
"
)
    
CommandArgument
(
"
-
-
distdir
"
help
=
"
Where
to
install
artifacts
to
.
"
)
    
def
artifact_install
(
        
self
        
source
=
None
        
skip_cache
=
False
        
tree
=
None
        
job
=
None
        
verbose
=
False
        
no_tests
=
False
        
symbols
=
False
        
host_bins
=
False
        
distdir
=
None
    
)
:
        
self
.
_set_log_level
(
verbose
)
        
artifacts
=
self
.
_make_artifacts
(
            
tree
=
tree
            
job
=
job
            
skip_cache
=
skip_cache
            
download_tests
=
not
no_tests
            
download_symbols
=
symbols
            
download_host_bins
=
host_bins
        
)
        
return
artifacts
.
install_from
(
source
distdir
or
self
.
distdir
)
    
ArtifactSubCommand
(
        
"
artifact
"
        
"
clear
-
cache
"
        
"
Delete
local
artifacts
and
reset
local
artifact
cache
.
"
    
)
    
def
artifact_clear_cache
(
self
tree
=
None
job
=
None
verbose
=
False
)
:
        
self
.
_set_log_level
(
verbose
)
        
artifacts
=
self
.
_make_artifacts
(
tree
=
tree
job
=
job
)
        
artifacts
.
clear_cache
(
)
        
return
0
    
SubCommand
(
"
artifact
"
"
toolchain
"
)
    
CommandArgument
(
        
"
-
-
verbose
"
"
-
v
"
action
=
"
store_true
"
help
=
"
Print
verbose
output
.
"
    
)
    
CommandArgument
(
        
"
-
-
cache
-
dir
"
        
metavar
=
"
DIR
"
        
help
=
"
Directory
where
to
store
the
artifacts
cache
"
    
)
    
CommandArgument
(
        
"
-
-
skip
-
cache
"
        
action
=
"
store_true
"
        
help
=
"
Skip
all
local
caches
to
force
re
-
fetching
remote
artifacts
.
"
        
default
=
False
    
)
    
CommandArgument
(
        
"
-
-
from
-
build
"
        
metavar
=
"
BUILD
"
        
nargs
=
"
+
"
        
help
=
"
Download
toolchains
resulting
from
the
given
build
(
s
)
;
"
        
"
BUILD
is
a
name
of
a
toolchain
task
e
.
g
.
linux64
-
clang
"
    
)
    
CommandArgument
(
        
"
-
-
tooltool
-
manifest
"
        
metavar
=
"
MANIFEST
"
        
help
=
"
Explicit
tooltool
manifest
to
process
"
    
)
    
CommandArgument
(
        
"
-
-
authentication
-
file
"
        
metavar
=
"
FILE
"
        
help
=
"
Use
the
RelengAPI
token
found
in
the
given
file
to
authenticate
"
    
)
    
CommandArgument
(
        
"
-
-
tooltool
-
url
"
metavar
=
"
URL
"
help
=
"
Use
the
given
url
as
tooltool
server
"
    
)
    
CommandArgument
(
        
"
-
-
no
-
unpack
"
action
=
"
store_true
"
help
=
"
Do
not
unpack
any
downloaded
file
"
    
)
    
CommandArgument
(
        
"
-
-
retry
"
type
=
int
default
=
4
help
=
"
Number
of
times
to
retry
failed
downloads
"
    
)
    
CommandArgument
(
        
"
-
-
artifact
-
manifest
"
        
metavar
=
"
FILE
"
        
help
=
"
Store
a
manifest
about
the
downloaded
taskcluster
artifacts
"
    
)
    
CommandArgument
(
        
"
files
"
        
nargs
=
"
*
"
        
help
=
"
A
list
of
files
to
download
in
the
form
path
task
-
id
in
"
        
"
addition
to
the
files
listed
in
the
tooltool
manifest
.
"
    
)
    
def
artifact_toolchain
(
        
self
        
verbose
=
False
        
cache_dir
=
None
        
skip_cache
=
False
        
from_build
=
(
)
        
tooltool_manifest
=
None
        
authentication_file
=
None
        
tooltool_url
=
None
        
no_unpack
=
False
        
retry
=
None
        
artifact_manifest
=
None
        
files
=
(
)
    
)
:
        
"
"
"
Download
cache
and
install
pre
-
built
toolchains
.
        
"
"
"
        
from
mozbuild
.
artifacts
import
ArtifactCache
        
from
mozbuild
.
action
.
tooltool
import
FileRecord
open_manifest
unpack_file
        
from
requests
.
adapters
import
HTTPAdapter
        
import
redo
        
import
requests
        
from
taskgraph
.
util
.
taskcluster
import
get_artifact_url
        
self
.
_set_log_level
(
verbose
)
        
#
Normally
we
'
d
use
self
.
log_manager
.
enable_unstructured
(
)
        
#
but
that
enables
all
logging
while
we
only
really
want
tooltool
'
s
        
#
and
it
also
makes
structured
log
output
twice
.
        
#
So
we
manually
do
what
it
does
and
limit
that
to
the
tooltool
        
#
logger
.
        
if
self
.
log_manager
.
terminal_handler
:
            
logging
.
getLogger
(
"
mozbuild
.
action
.
tooltool
"
)
.
addHandler
(
                
self
.
log_manager
.
terminal_handler
            
)
            
logging
.
getLogger
(
"
redo
"
)
.
addHandler
(
self
.
log_manager
.
terminal_handler
)
            
self
.
log_manager
.
terminal_handler
.
addFilter
(
                
self
.
log_manager
.
structured_filter
            
)
        
if
not
cache_dir
:
            
cache_dir
=
os
.
path
.
join
(
self
.
_mach_context
.
state_dir
"
toolchains
"
)
        
tooltool_url
=
(
tooltool_url
or
"
https
:
/
/
tooltool
.
mozilla
-
releng
.
net
"
)
.
rstrip
(
            
"
/
"
        
)
        
cache
=
ArtifactCache
(
cache_dir
=
cache_dir
log
=
self
.
log
skip_cache
=
skip_cache
)
        
if
authentication_file
:
            
with
open
(
authentication_file
"
rb
"
)
as
f
:
                
token
=
f
.
read
(
)
.
strip
(
)
            
class
TooltoolAuthenticator
(
HTTPAdapter
)
:
                
def
send
(
self
request
*
args
*
*
kwargs
)
:
                    
request
.
headers
[
"
Authorization
"
]
=
"
Bearer
{
}
"
.
format
(
token
)
                    
return
super
(
TooltoolAuthenticator
self
)
.
send
(
                        
request
*
args
*
*
kwargs
                    
)
            
cache
.
_download_manager
.
session
.
mount
(
tooltool_url
TooltoolAuthenticator
(
)
)
        
class
DownloadRecord
(
FileRecord
)
:
            
def
__init__
(
self
url
*
args
*
*
kwargs
)
:
                
super
(
DownloadRecord
self
)
.
__init__
(
*
args
*
*
kwargs
)
                
self
.
url
=
url
                
self
.
basename
=
self
.
filename
            
def
fetch_with
(
self
cache
)
:
                
self
.
filename
=
cache
.
fetch
(
self
.
url
)
                
return
self
.
filename
            
def
validate
(
self
)
:
                
if
self
.
size
is
None
and
self
.
digest
is
None
:
                    
return
True
                
return
super
(
DownloadRecord
self
)
.
validate
(
)
        
class
ArtifactRecord
(
DownloadRecord
)
:
            
def
__init__
(
self
task_id
artifact_name
)
:
                
for
_
in
redo
.
retrier
(
attempts
=
retry
+
1
sleeptime
=
60
)
:
                    
cot
=
cache
.
_download_manager
.
session
.
get
(
                        
get_artifact_url
(
task_id
"
public
/
chain
-
of
-
trust
.
json
"
)
                    
)
                    
if
cot
.
status_code
>
=
500
:
                        
continue
                    
cot
.
raise_for_status
(
)
                    
break
                
else
:
                    
cot
.
raise_for_status
(
)
                
digest
=
algorithm
=
None
                
data
=
json
.
loads
(
cot
.
content
)
                
for
algorithm
digest
in
(
                    
data
.
get
(
"
artifacts
"
{
}
)
.
get
(
artifact_name
{
}
)
.
items
(
)
                
)
:
                    
pass
                
name
=
os
.
path
.
basename
(
artifact_name
)
                
artifact_url
=
get_artifact_url
(
                    
task_id
                    
artifact_name
                    
use_proxy
=
not
artifact_name
.
startswith
(
"
public
/
"
)
                
)
                
super
(
ArtifactRecord
self
)
.
__init__
(
                    
artifact_url
name
None
digest
algorithm
unpack
=
True
                
)
        
records
=
OrderedDict
(
)
        
downloaded
=
[
]
        
if
tooltool_manifest
:
            
manifest
=
open_manifest
(
tooltool_manifest
)
            
for
record
in
manifest
.
file_records
:
                
url
=
"
{
}
/
{
}
/
{
}
"
.
format
(
tooltool_url
record
.
algorithm
record
.
digest
)
                
records
[
record
.
filename
]
=
DownloadRecord
(
                    
url
                    
record
.
filename
                    
record
.
size
                    
record
.
digest
                    
record
.
algorithm
                    
unpack
=
record
.
unpack
                    
version
=
record
.
version
                    
visibility
=
record
.
visibility
                
)
        
if
from_build
:
            
if
"
MOZ_AUTOMATION
"
in
os
.
environ
:
                
self
.
log
(
                    
logging
.
ERROR
                    
"
artifact
"
                    
{
}
                    
"
Do
not
use
-
-
from
-
build
in
automation
;
all
dependencies
"
                    
"
should
be
determined
in
the
decision
task
.
"
                
)
                
return
1
            
from
taskgraph
.
optimize
import
IndexSearch
            
from
taskgraph
.
parameters
import
Parameters
            
from
taskgraph
.
generator
import
load_tasks_for_kind
            
params
=
Parameters
(
                
level
=
os
.
environ
.
get
(
"
MOZ_SCM_LEVEL
"
"
3
"
)
strict
=
False
            
)
            
root_dir
=
mozpath
.
join
(
self
.
topsrcdir
"
taskcluster
/
ci
"
)
            
toolchains
=
load_tasks_for_kind
(
params
"
toolchain
"
root_dir
=
root_dir
)
            
aliases
=
{
}
            
for
t
in
toolchains
.
values
(
)
:
                
alias
=
t
.
attributes
.
get
(
"
toolchain
-
alias
"
)
                
if
alias
:
                    
aliases
[
"
toolchain
-
{
}
"
.
format
(
alias
)
]
=
t
.
task
[
"
metadata
"
]
[
"
name
"
]
            
for
b
in
from_build
:
                
user_value
=
b
                
if
not
b
.
startswith
(
"
toolchain
-
"
)
:
                    
b
=
"
toolchain
-
{
}
"
.
format
(
b
)
                
task
=
toolchains
.
get
(
aliases
.
get
(
b
b
)
)
                
if
not
task
:
                    
self
.
log
(
                        
logging
.
ERROR
                        
"
artifact
"
                        
{
"
build
"
:
user_value
}
                        
"
Could
not
find
a
toolchain
build
named
{
build
}
"
                    
)
                    
return
1
                
task_id
=
IndexSearch
(
)
.
should_replace_task
(
                    
task
{
}
task
.
optimization
.
get
(
"
index
-
search
"
[
]
)
                
)
                
artifact_name
=
task
.
attributes
.
get
(
"
toolchain
-
artifact
"
)
                
if
task_id
in
(
True
False
)
or
not
artifact_name
:
                    
self
.
log
(
                        
logging
.
ERROR
                        
"
artifact
"
                        
{
"
build
"
:
user_value
}
                        
"
Could
not
find
artifacts
for
a
toolchain
build
"
                        
"
named
{
build
}
.
Local
commits
and
other
changes
"
                        
"
in
your
checkout
may
cause
this
error
.
Try
"
                        
"
updating
to
a
fresh
checkout
of
mozilla
-
central
"
                        
"
to
use
artifact
builds
.
"
                    
)
                    
return
1
                
record
=
ArtifactRecord
(
task_id
artifact_name
)
                
records
[
record
.
filename
]
=
record
        
#
Handle
the
list
of
files
of
the
form
path
task
-
id
on
the
command
        
#
line
.
Each
of
those
give
a
path
to
an
artifact
to
download
.
        
for
f
in
files
:
            
if
"
"
not
in
f
:
                
self
.
log
(
                    
logging
.
ERROR
                    
"
artifact
"
                    
{
}
                    
"
Expected
a
list
of
files
of
the
form
path
task
-
id
"
                
)
                
return
1
            
name
task_id
=
f
.
rsplit
(
"
"
1
)
            
record
=
ArtifactRecord
(
task_id
name
)
            
records
[
record
.
filename
]
=
record
        
for
record
in
records
.
itervalues
(
)
:
            
self
.
log
(
                
logging
.
INFO
                
"
artifact
"
                
{
"
name
"
:
record
.
basename
}
                
"
Downloading
{
name
}
"
            
)
            
valid
=
False
            
#
sleeptime
is
60
per
retry
.
py
used
by
tooltool_wrapper
.
sh
            
for
attempt
_
in
enumerate
(
redo
.
retrier
(
attempts
=
retry
+
1
sleeptime
=
60
)
)
:
                
try
:
                    
record
.
fetch_with
(
cache
)
                
except
(
                    
requests
.
exceptions
.
HTTPError
                    
requests
.
exceptions
.
ChunkedEncodingError
                    
requests
.
exceptions
.
ConnectionError
                
)
as
e
:
                    
if
isinstance
(
e
requests
.
exceptions
.
HTTPError
)
:
                        
#
The
relengapi
proxy
likes
to
return
error
400
bad
request
                        
#
which
seems
improbably
to
be
due
to
our
(
simple
)
GET
                        
#
being
borked
.
                        
status
=
e
.
response
.
status_code
                        
should_retry
=
status
>
=
500
or
status
=
=
400
                    
else
:
                        
should_retry
=
True
                    
if
should_retry
or
attempt
<
retry
:
                        
level
=
logging
.
WARN
                    
else
:
                        
level
=
logging
.
ERROR
                    
#
e
.
message
is
not
always
a
string
so
convert
it
first
.
                    
self
.
log
(
level
"
artifact
"
{
}
str
(
e
.
message
)
)
                    
if
not
should_retry
:
                        
break
                    
if
attempt
<
retry
:
                        
self
.
log
(
                            
logging
.
INFO
"
artifact
"
{
}
"
Will
retry
in
a
moment
.
.
.
"
                        
)
                    
continue
                
try
:
                    
valid
=
record
.
validate
(
)
                
except
Exception
:
                    
pass
                
if
not
valid
:
                    
os
.
unlink
(
record
.
filename
)
                    
if
attempt
<
retry
:
                        
self
.
log
(
                            
logging
.
INFO
                            
"
artifact
"
                            
{
}
                            
"
Corrupt
download
.
Will
retry
in
a
moment
.
.
.
"
                        
)
                    
continue
                
downloaded
.
append
(
record
)
                
break
            
if
not
valid
:
                
self
.
log
(
                    
logging
.
ERROR
                    
"
artifact
"
                    
{
"
name
"
:
record
.
basename
}
                    
"
Failed
to
download
{
name
}
"
                
)
                
return
1
        
artifacts
=
{
}
if
artifact_manifest
else
None
        
for
record
in
downloaded
:
            
local
=
os
.
path
.
join
(
os
.
getcwd
(
)
record
.
basename
)
            
if
os
.
path
.
exists
(
local
)
:
                
os
.
unlink
(
local
)
            
#
unpack_file
needs
the
file
with
its
final
name
to
work
            
#
(
https
:
/
/
github
.
com
/
mozilla
/
build
-
tooltool
/
issues
/
38
)
so
we
            
#
need
to
copy
it
even
though
we
remove
it
later
.
Use
hard
links
            
#
when
possible
.
            
try
:
                
os
.
link
(
record
.
filename
local
)
            
except
Exception
:
                
shutil
.
copy
(
record
.
filename
local
)
            
#
Keep
a
sha256
of
each
downloaded
file
for
the
chain
-
of
-
trust
            
#
validation
.
            
if
artifact_manifest
is
not
None
:
                
with
open
(
local
)
as
fh
:
                    
h
=
hashlib
.
sha256
(
)
                    
while
True
:
                        
data
=
fh
.
read
(
1024
*
1024
)
                        
if
not
data
:
                            
break
                        
h
.
update
(
data
)
                
artifacts
[
record
.
url
]
=
{
"
sha256
"
:
h
.
hexdigest
(
)
}
            
if
record
.
unpack
and
not
no_unpack
:
                
unpack_file
(
local
)
                
os
.
unlink
(
local
)
        
if
not
downloaded
:
            
self
.
log
(
logging
.
ERROR
"
artifact
"
{
}
"
Nothing
to
download
"
)
            
if
files
:
                
return
1
        
if
artifacts
:
            
ensureParentDir
(
artifact_manifest
)
            
with
open
(
artifact_manifest
"
w
"
)
as
fh
:
                
json
.
dump
(
artifacts
fh
indent
=
4
sort_keys
=
True
)
        
return
0
CommandProvider
class
StaticAnalysis
(
MachCommandBase
)
:
    
"
"
"
Utilities
for
running
C
+
+
static
analysis
checks
and
format
.
"
"
"
    
#
List
of
file
extension
to
consider
(
should
start
with
dot
)
    
_format_include_extensions
=
(
"
.
cpp
"
"
.
c
"
"
.
cc
"
"
.
h
"
"
.
m
"
"
.
mm
"
)
    
#
File
containing
all
paths
to
exclude
from
formatting
    
_format_ignore_file
=
"
.
clang
-
format
-
ignore
"
    
_clang_tidy_config
=
None
    
_cov_config
=
None
    
Command
(
        
"
static
-
analysis
"
        
category
=
"
testing
"
        
description
=
"
Run
C
+
+
static
analysis
checks
"
    
)
    
def
static_analysis
(
self
)
:
        
#
If
not
arguments
are
provided
just
print
a
help
message
.
        
mach
=
Mach
(
os
.
getcwd
(
)
)
        
mach
.
run
(
[
"
static
-
analysis
"
"
-
-
help
"
]
)
    
StaticAnalysisSubCommand
(
        
"
static
-
analysis
"
"
check
"
"
Run
the
checks
using
the
helper
tool
"
    
)
    
CommandArgument
(
        
"
source
"
        
nargs
=
"
*
"
        
default
=
[
"
.
*
"
]
        
help
=
"
Source
files
to
be
analyzed
(
regex
on
path
)
.
"
        
"
Can
be
omitted
in
which
case
the
entire
code
base
"
        
"
is
analyzed
.
The
source
argument
is
ignored
if
"
        
"
there
is
anything
fed
through
stdin
in
which
case
"
        
"
the
analysis
is
only
performed
on
the
files
changed
"
        
"
in
the
patch
streamed
through
stdin
.
This
is
called
"
        
"
the
diff
mode
.
"
    
)
    
CommandArgument
(
        
"
-
-
checks
"
        
"
-
c
"
        
default
=
"
-
*
"
        
metavar
=
"
checks
"
        
help
=
"
Static
analysis
checks
to
enable
.
By
default
this
enables
only
"
        
"
checks
that
are
published
here
:
https
:
/
/
mzl
.
la
/
2DRHeTh
but
can
be
any
"
        
"
clang
-
tidy
checks
syntax
.
"
    
)
    
CommandArgument
(
        
"
-
-
jobs
"
        
"
-
j
"
        
default
=
"
0
"
        
metavar
=
"
jobs
"
        
type
=
int
        
help
=
"
Number
of
concurrent
jobs
to
run
.
Default
is
the
number
of
CPUs
.
"
    
)
    
CommandArgument
(
        
"
-
-
strip
"
        
"
-
p
"
        
default
=
"
1
"
        
metavar
=
"
NUM
"
        
help
=
"
Strip
NUM
leading
components
from
file
names
in
diff
mode
.
"
    
)
    
CommandArgument
(
        
"
-
-
fix
"
        
"
-
f
"
        
default
=
False
        
action
=
"
store_true
"
        
help
=
"
Try
to
autofix
errors
detected
by
clang
-
tidy
checkers
.
"
    
)
    
CommandArgument
(
        
"
-
-
header
-
filter
"
        
"
-
h
-
f
"
        
default
=
"
"
        
metavar
=
"
header_filter
"
        
help
=
"
Regular
expression
matching
the
names
of
the
headers
to
"
        
"
output
diagnostics
from
.
Diagnostics
from
the
main
file
"
        
"
of
each
translation
unit
are
always
displayed
"
    
)
    
CommandArgument
(
        
"
-
-
output
"
"
-
o
"
default
=
None
help
=
"
Write
clang
-
tidy
output
in
a
file
"
    
)
    
CommandArgument
(
        
"
-
-
format
"
        
default
=
"
text
"
        
choices
=
(
"
text
"
"
json
"
)
        
help
=
"
Output
format
to
write
in
a
file
"
    
)
    
CommandArgument
(
        
"
-
-
outgoing
"
        
default
=
False
        
action
=
"
store_true
"
        
help
=
"
Run
static
analysis
checks
on
outgoing
files
from
mercurial
repository
"
    
)
    
def
check
(
        
self
        
source
=
None
        
jobs
=
2
        
strip
=
1
        
verbose
=
False
        
checks
=
"
-
*
"
        
fix
=
False
        
header_filter
=
"
"
        
output
=
None
        
format
=
"
text
"
        
outgoing
=
False
    
)
:
        
from
mozbuild
.
controller
.
building
import
(
            
StaticAnalysisFooter
            
StaticAnalysisOutputManager
        
)
        
self
.
_set_log_level
(
verbose
)
        
self
.
log_manager
.
enable_all_structured_loggers
(
)
        
rc
=
self
.
_get_clang_tools
(
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
return
rc
        
if
self
.
_is_version_eligible
(
)
is
False
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
You
'
re
using
an
old
version
of
clang
-
format
binary
.
"
                
"
Please
update
to
a
more
recent
one
by
running
:
'
.
/
mach
bootstrap
'
"
            
)
            
return
1
        
rc
=
self
.
_build_compile_db
(
verbose
=
verbose
)
        
rc
=
rc
or
self
.
_build_export
(
jobs
=
jobs
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
return
rc
        
#
Use
outgoing
files
instead
of
source
files
        
if
outgoing
:
            
repo
=
get_repository_object
(
self
.
topsrcdir
)
            
files
=
repo
.
get_outgoing_files
(
)
            
source
=
map
(
os
.
path
.
abspath
files
)
        
#
Split
in
several
chunks
to
avoid
hitting
Python
'
s
limit
of
100
groups
in
re
        
compile_db
=
json
.
loads
(
open
(
self
.
_compile_db
"
r
"
)
.
read
(
)
)
        
total
=
0
        
import
re
        
chunk_size
=
50
        
for
offset
in
range
(
0
len
(
source
)
chunk_size
)
:
            
source_chunks
=
source
[
offset
:
offset
+
chunk_size
]
            
name_re
=
re
.
compile
(
"
(
"
+
"
)
|
(
"
.
join
(
source_chunks
)
+
"
)
"
)
            
for
f
in
compile_db
:
                
if
name_re
.
search
(
f
[
"
file
"
]
)
:
                    
total
=
total
+
1
        
if
not
total
:
            
self
.
log
(
                
logging
.
INFO
                
"
static
-
analysis
"
                
{
}
                
"
There
are
no
files
eligible
for
analysis
.
Please
note
that
'
header
'
files
"
                
"
cannot
be
used
for
analysis
since
they
do
not
consist
compilation
units
.
"
            
)
            
return
0
        
cwd
=
self
.
topobjdir
        
self
.
_compilation_commands_path
=
self
.
topobjdir
        
if
self
.
_clang_tidy_config
is
None
:
            
self
.
_clang_tidy_config
=
self
.
_get_clang_tidy_config
(
)
        
args
=
self
.
_get_clang_tidy_command
(
            
checks
=
checks
            
header_filter
=
header_filter
            
sources
=
source
            
jobs
=
jobs
            
fix
=
fix
        
)
        
monitor
=
StaticAnalysisMonitor
(
            
self
.
topsrcdir
self
.
topobjdir
self
.
_clang_tidy_config
total
        
)
        
footer
=
StaticAnalysisFooter
(
self
.
log_manager
.
terminal
monitor
)
        
with
StaticAnalysisOutputManager
(
            
self
.
log_manager
monitor
footer
        
)
as
output_manager
:
            
rc
=
self
.
run_process
(
                
args
=
args
                
ensure_exit_code
=
False
                
line_handler
=
output_manager
.
on_line
                
cwd
=
cwd
            
)
            
self
.
log
(
                
logging
.
WARNING
                
"
warning_summary
"
                
{
"
count
"
:
len
(
monitor
.
warnings_db
)
}
                
"
{
count
}
warnings
present
.
"
            
)
            
#
Write
output
file
            
if
output
is
not
None
:
                
output_manager
.
write
(
output
format
)
        
if
rc
!
=
0
:
            
return
rc
        
#
if
we
are
building
firefox
for
android
it
might
be
nice
to
        
#
also
analyze
the
java
code
base
        
if
self
.
substs
[
"
MOZ_BUILD_APP
"
]
=
=
"
mobile
/
android
"
:
            
rc
=
self
.
check_java
(
source
jobs
strip
verbose
skip_export
=
True
)
        
return
rc
    
StaticAnalysisSubCommand
(
        
"
static
-
analysis
"
        
"
check
-
coverity
"
        
"
Run
coverity
static
-
analysis
tool
on
the
given
files
.
"
        
"
Can
only
be
run
by
automation
!
"
        
"
It
'
s
result
is
stored
as
an
json
file
on
the
artifacts
server
.
"
    
)
    
CommandArgument
(
        
"
source
"
        
nargs
=
"
*
"
        
default
=
[
]
        
help
=
"
Source
files
to
be
analyzed
by
Coverity
Static
Analysis
Tool
.
"
        
"
This
is
ran
only
in
automation
.
"
    
)
    
CommandArgument
(
        
"
-
-
output
"
        
"
-
o
"
        
default
=
None
        
help
=
"
Write
coverity
output
translated
to
json
output
in
a
file
"
    
)
    
CommandArgument
(
        
"
-
-
coverity_output_path
"
        
"
-
co
"
        
default
=
None
        
help
=
"
Path
where
to
write
coverity
results
as
cov
-
results
.
json
.
"
        
"
If
no
path
is
specified
the
default
path
from
the
coverity
working
directory
"
        
"
~
.
/
mozbuild
/
coverity
is
used
.
"
    
)
    
CommandArgument
(
        
"
-
-
outgoing
"
        
default
=
False
        
action
=
"
store_true
"
        
help
=
"
Run
coverity
on
outgoing
files
from
mercurial
or
git
repository
"
    
)
    
def
check_coverity
(
        
self
        
source
=
[
]
        
output
=
None
        
coverity_output_path
=
None
        
outgoing
=
False
        
verbose
=
False
    
)
:
        
self
.
_set_log_level
(
verbose
)
        
self
.
log_manager
.
enable_all_structured_loggers
(
)
        
if
"
MOZ_AUTOMATION
"
not
in
os
.
environ
:
            
self
.
log
(
                
logging
.
INFO
                
"
static
-
analysis
"
                
{
}
                
"
Coverity
based
static
-
analysis
cannot
be
ran
outside
automation
.
"
            
)
            
return
        
#
Use
outgoing
files
instead
of
source
files
        
if
outgoing
:
            
repo
=
get_repository_object
(
self
.
topsrcdir
)
            
files
=
repo
.
get_outgoing_files
(
)
            
source
=
map
(
os
.
path
.
abspath
files
)
        
if
len
(
source
)
=
=
0
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
There
are
no
files
that
coverity
can
use
to
scan
.
"
            
)
            
return
0
        
rc
=
self
.
_build_compile_db
(
verbose
=
verbose
)
        
rc
=
rc
or
self
.
_build_export
(
jobs
=
2
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
return
rc
        
commands_list
=
self
.
get_files_with_commands
(
source
)
        
if
len
(
commands_list
)
=
=
0
:
            
self
.
log
(
                
logging
.
INFO
                
"
static
-
analysis
"
                
{
}
                
"
There
are
no
files
that
need
to
be
analyzed
.
"
            
)
            
return
0
        
#
Load
the
configuration
file
for
coverity
static
-
analysis
        
#
For
the
moment
we
store
only
the
reliability
index
for
each
checker
        
#
as
the
rest
is
managed
on
the
https
:
/
/
github
.
com
/
mozilla
/
release
-
services
side
.
        
self
.
_cov_config
=
self
.
_get_cov_config
(
)
        
rc
=
self
.
setup_coverity
(
)
        
if
rc
!
=
0
:
            
return
rc
        
#
First
run
cov
-
run
-
desktop
-
-
setup
in
order
to
setup
the
analysis
env
        
cmd
=
[
self
.
cov_run_desktop
"
-
-
setup
"
]
        
self
.
log
(
            
logging
.
INFO
            
"
static
-
analysis
"
            
{
}
            
"
Running
{
}
-
-
setup
"
.
format
(
self
.
cov_run_desktop
)
        
)
        
rc
=
self
.
run_process
(
args
=
cmd
cwd
=
self
.
cov_path
pass_thru
=
True
)
        
if
rc
!
=
0
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
Running
{
}
-
-
setup
failed
!
"
.
format
(
self
.
cov_run_desktop
)
            
)
            
return
rc
        
#
Run
cov
-
configure
for
clang
        
cmd
=
[
self
.
cov_configure
"
-
-
clang
"
]
        
self
.
log
(
            
logging
.
INFO
            
"
static
-
analysis
"
            
{
}
            
"
Running
{
}
-
-
clang
"
.
format
(
self
.
cov_configure
)
        
)
        
rc
=
self
.
run_process
(
args
=
cmd
cwd
=
self
.
cov_path
pass_thru
=
True
)
        
if
rc
!
=
0
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
Running
{
}
-
-
clang
failed
!
"
.
format
(
self
.
cov_configure
)
            
)
            
return
rc
        
#
For
each
element
in
commands_list
run
cov
-
translate
        
for
element
in
commands_list
:
            
cmd
=
[
self
.
cov_translate
"
-
-
dir
"
self
.
cov_idir_path
]
+
element
[
                
"
command
"
            
]
.
split
(
"
"
)
            
self
.
log
(
                
logging
.
INFO
                
"
static
-
analysis
"
                
{
}
                
"
Running
Coverity
Translate
for
{
}
"
.
format
(
cmd
)
            
)
            
rc
=
self
.
run_process
(
args
=
cmd
cwd
=
element
[
"
directory
"
]
pass_thru
=
True
)
            
if
rc
!
=
0
:
                
self
.
log
(
                    
logging
.
ERROR
                    
"
static
-
analysis
"
                    
{
}
                    
"
Running
Coverity
Translate
failed
for
{
}
"
.
format
(
cmd
)
                
)
                
return
cmd
        
if
coverity_output_path
is
None
:
            
cov_result
=
mozpath
.
join
(
self
.
cov_state_path
"
cov
-
results
.
json
"
)
        
else
:
            
cov_result
=
mozpath
.
join
(
coverity_output_path
"
cov
-
results
.
json
"
)
        
#
Once
the
capture
is
performed
we
need
to
do
the
actual
Coverity
Desktop
analysis
        
cmd
=
[
            
self
.
cov_run_desktop
            
"
-
-
json
-
output
-
v6
"
            
cov_result
            
"
-
-
analyze
-
captured
-
source
"
        
]
        
self
.
log
(
            
logging
.
INFO
            
"
static
-
analysis
"
            
{
}
            
"
Running
Coverity
Analysis
for
{
}
"
.
format
(
cmd
)
        
)
        
rc
=
self
.
run_process
(
cmd
cwd
=
self
.
cov_state_path
pass_thru
=
True
)
        
if
rc
!
=
0
:
            
self
.
log
(
logging
.
ERROR
"
static
-
analysis
"
{
}
"
Coverity
Analysis
failed
!
"
)
        
if
output
is
not
None
:
            
self
.
dump_cov_artifact
(
cov_result
source
output
)
    
def
get_reliability_index_for_cov_checker
(
self
checker_name
)
:
        
if
self
.
_cov_config
is
None
:
            
self
.
log
(
                
logging
.
INFO
                
"
static
-
analysis
"
                
{
}
                
"
Coverity
config
file
not
found
"
                
"
using
default
-
value
'
reliablity
'
=
medium
.
for
checker
{
}
"
.
format
(
                    
checker_name
                
)
            
)
            
return
"
medium
"
        
checkers
=
self
.
_cov_config
[
"
coverity_checkers
"
]
        
if
checker_name
not
in
checkers
:
            
self
.
log
(
                
logging
.
INFO
                
"
static
-
analysis
"
                
{
}
                
"
Coverity
checker
{
}
not
found
to
determine
reliability
index
.
"
                
"
For
the
moment
we
shall
use
the
default
'
reliablity
'
=
medium
.
"
.
format
(
                    
checker_name
                
)
            
)
            
return
"
medium
"
        
if
"
reliability
"
not
in
checkers
[
checker_name
]
:
            
#
This
checker
doesn
'
t
have
a
reliability
index
            
self
.
log
(
                
logging
.
INFO
                
"
static
-
analysis
"
                
{
}
                
"
Coverity
checker
{
}
doesn
'
t
have
a
reliability
index
set
"
                
"
field
'
reliability
is
missing
'
please
cosinder
adding
it
.
"
                
"
For
the
moment
we
shall
use
the
default
'
reliablity
'
=
medium
.
"
.
format
(
                    
checker_name
                
)
            
)
            
return
"
medium
"
        
return
checkers
[
checker_name
]
[
"
reliability
"
]
    
def
dump_cov_artifact
(
self
cov_results
source
output
)
:
        
#
Parse
Coverity
json
into
structured
issues
        
with
open
(
cov_results
)
as
f
:
            
result
=
json
.
load
(
f
)
            
#
Parse
the
issues
to
a
standard
json
format
            
issues_dict
=
{
"
files
"
:
{
}
}
            
files_list
=
issues_dict
[
"
files
"
]
            
def
build_element
(
issue
)
:
                
#
We
look
only
for
main
event
                
event_path
=
next
(
                    
(
event
for
event
in
issue
[
"
events
"
]
if
event
[
"
main
"
]
is
True
)
None
                
)
                
dict_issue
=
{
                    
"
line
"
:
issue
[
"
mainEventLineNumber
"
]
                    
"
flag
"
:
issue
[
"
checkerName
"
]
                    
"
message
"
:
event_path
[
"
eventDescription
"
]
                    
"
reliability
"
:
self
.
get_reliability_index_for_cov_checker
(
                        
issue
[
"
checkerName
"
]
                    
)
                    
"
extra
"
:
{
                        
"
category
"
:
issue
[
"
checkerProperties
"
]
[
"
category
"
]
                        
"
stateOnServer
"
:
issue
[
"
stateOnServer
"
]
                        
"
stack
"
:
[
]
                    
}
                
}
                
#
Embed
all
events
into
extra
message
                
for
event
in
issue
[
"
events
"
]
:
                    
dict_issue
[
"
extra
"
]
[
"
stack
"
]
.
append
(
                        
{
                            
"
file_path
"
:
event
[
"
strippedFilePathname
"
]
                            
"
line_number
"
:
event
[
"
lineNumber
"
]
                            
"
path_type
"
:
event
[
"
eventTag
"
]
                            
"
description
"
:
event
[
"
eventDescription
"
]
                        
}
                    
)
                
return
dict_issue
            
for
issue
in
result
[
"
issues
"
]
:
                
path
=
self
.
cov_is_file_in_source
(
                    
issue
[
"
strippedMainEventFilePathname
"
]
source
                
)
                
if
path
is
None
:
                    
#
Since
we
skip
a
result
we
should
log
it
                    
self
.
log
(
                        
logging
.
INFO
                        
"
static
-
analysis
"
                        
{
}
                        
"
Skipping
CID
:
{
0
}
from
file
:
{
1
}
since
it
'
s
not
related
"
                        
"
with
the
current
patch
.
"
.
format
(
                            
issue
[
"
stateOnServer
"
]
[
"
cid
"
]
                            
issue
[
"
strippedMainEventFilePathname
"
]
                        
)
                    
)
                    
continue
                
if
path
in
files_list
:
                    
files_list
[
path
]
[
"
warnings
"
]
.
append
(
build_element
(
issue
)
)
                
else
:
                    
files_list
[
path
]
=
{
"
warnings
"
:
[
build_element
(
issue
)
]
}
            
with
open
(
output
"
w
"
)
as
f
:
                
json
.
dump
(
issues_dict
f
)
    
def
get_coverity_secrets
(
self
)
:
        
from
taskgraph
.
util
.
taskcluster
import
get_root_url
        
secret_name
=
"
project
/
relman
/
coverity
"
        
secrets_url
=
"
{
}
/
secrets
/
v1
/
secret
/
{
}
"
.
format
(
get_root_url
(
True
)
secret_name
)
        
self
.
log
(
            
logging
.
INFO
            
"
static
-
analysis
"
            
{
}
            
'
Using
symbol
upload
token
from
the
secrets
service
:
"
{
}
"
'
.
format
(
                
secrets_url
            
)
        
)
        
import
requests
        
res
=
requests
.
get
(
secrets_url
)
        
res
.
raise_for_status
(
)
        
secret
=
res
.
json
(
)
        
cov_config
=
secret
[
"
secret
"
]
if
"
secret
"
in
secret
else
None
        
if
cov_config
is
None
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
Ill
formatted
secret
for
Coverity
.
Aborting
analysis
.
"
            
)
            
return
1
        
self
.
cov_analysis_url
=
cov_config
.
get
(
"
package_url
"
)
        
self
.
cov_package_name
=
cov_config
.
get
(
"
package_name
"
)
        
self
.
cov_url
=
cov_config
.
get
(
"
server_url
"
)
        
self
.
cov_auth
=
cov_config
.
get
(
"
auth_key
"
)
        
self
.
cov_package_ver
=
cov_config
.
get
(
"
package_ver
"
)
        
self
.
cov_full_stack
=
cov_config
.
get
(
"
full_stack
"
False
)
        
return
0
    
def
download_coverity
(
self
)
:
        
if
(
            
self
.
cov_url
is
None
            
or
self
.
cov_analysis_url
is
None
            
or
self
.
cov_auth
is
None
        
)
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
Missing
Coverity
secret
on
try
job
!
"
            
)
            
return
1
        
COVERITY_CONFIG
=
"
"
"
        
{
            
"
type
"
:
"
Coverity
configuration
"
            
"
format_version
"
:
1
            
"
settings
"
:
{
            
"
server
"
:
{
                
"
host
"
:
"
%
s
"
                
"
ssl
"
:
true
                
"
on_new_cert
"
:
"
trust
"
                
"
auth_key_file
"
:
"
%
s
"
            
}
            
"
stream
"
:
"
Firefox
"
            
"
cov_run_desktop
"
:
{
                
"
build_cmd
"
:
[
]
                
"
clean_cmd
"
:
[
]
            
}
            
}
        
}
        
"
"
"
        
#
Generate
the
coverity
.
conf
and
auth
files
        
cov_auth_path
=
mozpath
.
join
(
self
.
cov_state_path
"
auth
"
)
        
cov_setup_path
=
mozpath
.
join
(
self
.
cov_state_path
"
coverity
.
conf
"
)
        
cov_conf
=
COVERITY_CONFIG
%
(
self
.
cov_url
cov_auth_path
)
        
def
download
(
artifact_url
target
)
:
            
import
requests
            
resp
=
requests
.
get
(
artifact_url
verify
=
False
stream
=
True
)
            
resp
.
raise_for_status
(
)
            
#
Extract
archive
into
destination
            
with
tarfile
.
open
(
fileobj
=
io
.
BytesIO
(
resp
.
content
)
)
as
tar
:
                
tar
.
extractall
(
target
)
        
download
(
self
.
cov_analysis_url
self
.
cov_state_path
)
        
with
open
(
cov_auth_path
"
w
"
)
as
f
:
            
f
.
write
(
self
.
cov_auth
)
        
#
Modify
it
'
s
permission
to
600
        
os
.
chmod
(
cov_auth_path
0o600
)
        
with
open
(
cov_setup_path
"
a
"
)
as
f
:
            
f
.
write
(
cov_conf
)
    
def
setup_coverity
(
self
force_download
=
True
)
:
        
rc
config
_
=
self
.
_get_config_environment
(
)
        
rc
=
rc
or
self
.
get_coverity_secrets
(
)
        
if
rc
!
=
0
:
            
return
rc
        
#
Create
a
directory
in
mozbuild
where
we
setup
coverity
        
self
.
cov_state_path
=
mozpath
.
join
(
self
.
_mach_context
.
state_dir
"
coverity
"
)
        
if
force_download
is
True
and
os
.
path
.
exists
(
self
.
cov_state_path
)
:
            
shutil
.
rmtree
(
self
.
cov_state_path
)
        
os
.
mkdir
(
self
.
cov_state_path
)
        
#
Download
everything
that
we
need
for
Coverity
from
out
private
instance
        
self
.
download_coverity
(
)
        
self
.
cov_path
=
mozpath
.
join
(
self
.
cov_state_path
self
.
cov_package_name
)
        
self
.
cov_run_desktop
=
mozpath
.
join
(
self
.
cov_path
"
bin
"
"
cov
-
run
-
desktop
"
)
        
self
.
cov_translate
=
mozpath
.
join
(
self
.
cov_path
"
bin
"
"
cov
-
translate
"
)
        
self
.
cov_configure
=
mozpath
.
join
(
self
.
cov_path
"
bin
"
"
cov
-
configure
"
)
        
self
.
cov_work_path
=
mozpath
.
join
(
self
.
cov_state_path
"
data
-
coverity
"
)
        
self
.
cov_idir_path
=
mozpath
.
join
(
            
self
.
cov_work_path
self
.
cov_package_ver
"
idir
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
self
.
cov_path
)
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
Missing
Coverity
in
{
}
"
.
format
(
self
.
cov_path
)
            
)
            
return
1
        
return
0
    
def
cov_is_file_in_source
(
self
abs_path
source
)
:
        
#
We
have
as
an
input
an
absolute
path
for
whom
we
verify
if
it
'
s
a
symlink
        
#
if
so
we
follow
that
symlink
and
we
match
it
with
elements
from
source
.
        
#
If
the
match
is
done
we
return
abs_path
otherwise
None
        
assert
isinstance
(
source
list
)
        
if
os
.
path
.
islink
(
abs_path
)
:
            
abs_path
=
os
.
path
.
realpath
(
abs_path
)
        
if
abs_path
in
source
:
            
return
abs_path
        
return
None
    
def
get_files_with_commands
(
self
source
)
:
        
"
"
"
        
Returns
an
array
of
dictionaries
having
file_path
with
build
command
        
"
"
"
        
compile_db
=
json
.
load
(
open
(
self
.
_compile_db
"
r
"
)
)
        
commands_list
=
[
]
        
for
f
in
source
:
            
#
It
must
be
a
C
/
C
+
+
file
            
_
ext
=
os
.
path
.
splitext
(
f
)
            
if
ext
.
lower
(
)
not
in
self
.
_format_include_extensions
:
                
self
.
log
(
logging
.
INFO
"
static
-
analysis
"
{
}
"
Skipping
{
}
"
.
format
(
f
)
)
                
continue
            
file_with_abspath
=
os
.
path
.
join
(
self
.
topsrcdir
f
)
            
for
f
in
compile_db
:
                
#
Found
for
a
file
that
we
are
looking
                
if
file_with_abspath
=
=
f
[
"
file
"
]
:
                    
commands_list
.
append
(
f
)
        
return
commands_list
    
StaticAnalysisSubCommand
(
        
"
static
-
analysis
"
"
check
-
java
"
"
Run
infer
on
the
java
codebase
.
"
    
)
    
CommandArgument
(
        
"
source
"
        
nargs
=
"
*
"
        
default
=
[
"
mobile
"
]
        
help
=
"
Source
files
to
be
analyzed
.
"
        
"
Can
be
omitted
in
which
case
the
entire
code
base
"
        
"
is
analyzed
.
The
source
argument
is
ignored
if
"
        
"
there
is
anything
fed
through
stdin
in
which
case
"
        
"
the
analysis
is
only
performed
on
the
files
changed
"
        
"
in
the
patch
streamed
through
stdin
.
This
is
called
"
        
"
the
diff
mode
.
"
    
)
    
CommandArgument
(
        
"
-
-
checks
"
        
"
-
c
"
        
default
=
[
]
        
metavar
=
"
checks
"
        
nargs
=
"
*
"
        
help
=
"
Static
analysis
checks
to
enable
.
"
    
)
    
CommandArgument
(
        
"
-
-
jobs
"
        
"
-
j
"
        
default
=
"
0
"
        
metavar
=
"
jobs
"
        
type
=
int
        
help
=
"
Number
of
concurrent
jobs
to
run
.
"
"
Default
is
the
number
of
CPUs
.
"
    
)
    
CommandArgument
(
        
"
-
-
task
"
        
"
-
t
"
        
type
=
str
        
default
=
"
compileWithGeckoBinariesDebugSources
"
        
help
=
"
Which
gradle
tasks
to
use
to
compile
the
java
codebase
.
"
    
)
    
CommandArgument
(
        
"
-
-
outgoing
"
        
default
=
False
        
action
=
"
store_true
"
        
help
=
"
Run
infer
checks
on
outgoing
files
from
repository
"
    
)
    
CommandArgument
(
"
-
-
output
"
default
=
None
help
=
"
Write
infer
json
output
in
a
file
"
)
    
def
check_java
(
        
self
        
source
=
[
"
mobile
"
]
        
jobs
=
2
        
strip
=
1
        
verbose
=
False
        
checks
=
[
]
        
task
=
"
compileWithGeckoBinariesDebugSources
"
        
skip_export
=
False
        
outgoing
=
False
        
output
=
None
    
)
:
        
self
.
_set_log_level
(
verbose
)
        
self
.
log_manager
.
enable_all_structured_loggers
(
)
        
if
self
.
substs
[
"
MOZ_BUILD_APP
"
]
!
=
"
mobile
/
android
"
:
            
self
.
log
(
                
logging
.
WARNING
                
"
static
-
analysis
"
                
{
}
                
"
Cannot
check
java
source
code
unless
you
are
building
for
android
!
"
            
)
            
return
1
        
rc
=
self
.
_check_for_java
(
)
        
if
rc
!
=
0
:
            
return
1
        
if
output
is
not
None
:
            
output
=
os
.
path
.
abspath
(
output
)
            
if
not
os
.
path
.
isdir
(
os
.
path
.
dirname
(
output
)
)
:
                
self
.
log
(
                    
logging
.
WARNING
                    
"
static
-
analysis
"
                    
{
}
                    
"
Missing
report
destination
folder
for
{
}
"
.
format
(
output
)
                
)
        
#
if
source
contains
the
whole
mobile
folder
then
we
just
have
to
        
#
analyze
everything
        
check_all
=
any
(
i
.
rstrip
(
os
.
sep
)
.
split
(
os
.
sep
)
[
-
1
]
=
=
"
mobile
"
for
i
in
source
)
        
#
gather
all
java
sources
from
the
source
variable
        
java_sources
=
[
]
        
if
outgoing
:
            
repo
=
get_repository_object
(
self
.
topsrcdir
)
            
java_sources
=
self
.
_get_java_files
(
repo
.
get_outgoing_files
(
)
)
            
if
not
java_sources
:
                
self
.
log
(
                    
logging
.
WARNING
                    
"
static
-
analysis
"
                    
{
}
                    
"
No
outgoing
Java
files
to
check
"
                
)
                
return
0
        
elif
not
check_all
:
            
java_sources
=
self
.
_get_java_files
(
source
)
            
if
not
java_sources
:
                
return
0
        
if
not
skip_export
:
            
rc
=
self
.
_build_export
(
jobs
=
jobs
verbose
=
verbose
)
            
if
rc
!
=
0
:
                
return
rc
        
rc
=
self
.
_get_infer
(
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
self
.
log
(
                
logging
.
WARNING
                
"
static
-
analysis
"
                
{
}
                
"
This
command
is
only
available
for
linux64
!
"
            
)
            
return
rc
        
#
which
checkers
to
use
and
which
folders
to
exclude
        
all_checkers
third_party_path
=
self
.
_get_infer_config
(
)
        
checkers
excludes
=
self
.
_get_infer_args
(
            
checks
=
checks
or
all_checkers
third_party_path
=
third_party_path
        
)
        
rc
=
rc
or
self
.
_gradle
(
[
"
clean
"
]
)
#
clean
so
that
we
can
recompile
        
#
infer
capture
command
        
capture_cmd
=
[
self
.
_infer_path
"
capture
"
]
+
excludes
+
[
"
-
-
"
]
        
rc
=
rc
or
self
.
_gradle
(
[
task
]
infer_args
=
capture_cmd
verbose
=
verbose
)
        
tmp_file
args
=
self
.
_get_infer_source_args
(
java_sources
)
        
#
infer
analyze
command
        
analysis_cmd
=
[
self
.
_infer_path
"
analyze
"
"
-
-
keep
-
going
"
]
+
checkers
+
args
        
rc
=
rc
or
self
.
run_process
(
            
args
=
analysis_cmd
cwd
=
self
.
topsrcdir
pass_thru
=
True
        
)
        
if
tmp_file
:
            
tmp_file
.
close
(
)
        
#
Copy
the
infer
report
        
report_path
=
os
.
path
.
join
(
self
.
topsrcdir
"
infer
-
out
"
"
report
.
json
"
)
        
if
output
is
not
None
and
os
.
path
.
exists
(
report_path
)
:
            
shutil
.
copy
(
report_path
output
)
            
self
.
log
(
                
logging
.
INFO
                
"
static
-
analysis
"
                
{
}
                
"
Report
available
in
{
}
"
.
format
(
output
)
            
)
        
return
rc
    
def
_get_java_files
(
self
sources
)
:
        
java_sources
=
[
]
        
for
i
in
sources
:
            
f
=
mozpath
.
join
(
self
.
topsrcdir
i
)
            
if
os
.
path
.
isdir
(
f
)
:
                
for
root
dirs
files
in
os
.
walk
(
f
)
:
                    
dirs
.
sort
(
)
                    
for
file
in
sorted
(
files
)
:
                        
if
file
.
endswith
(
"
.
java
"
)
:
                            
java_sources
.
append
(
mozpath
.
join
(
root
file
)
)
            
elif
f
.
endswith
(
"
.
java
"
)
:
                
java_sources
.
append
(
f
)
        
return
java_sources
    
def
_get_infer_source_args
(
self
sources
)
:
        
"
"
"
Return
the
arguments
to
only
analyze
<
sources
>
"
"
"
        
if
not
sources
:
            
return
(
None
[
]
)
        
#
create
a
temporary
file
in
which
we
place
all
sources
        
#
this
is
used
by
the
analysis
command
to
only
analyze
certain
files
        
f
=
tempfile
.
NamedTemporaryFile
(
)
        
for
source
in
sources
:
            
f
.
write
(
source
+
"
\
n
"
)
        
f
.
flush
(
)
        
return
(
f
[
"
-
-
changed
-
files
-
index
"
f
.
name
]
)
    
def
_get_infer_config
(
self
)
:
        
"
"
"
Load
the
infer
config
file
.
"
"
"
        
checkers
=
[
]
        
tp_path
=
"
"
        
with
open
(
mozpath
.
join
(
self
.
topsrcdir
"
tools
"
"
infer
"
"
config
.
yaml
"
)
)
as
f
:
            
try
:
                
config
=
yaml
.
safe_load
(
f
)
                
for
item
in
config
[
"
infer_checkers
"
]
:
                    
if
item
[
"
publish
"
]
:
                        
checkers
.
append
(
item
[
"
name
"
]
)
                
tp_path
=
mozpath
.
join
(
self
.
topsrcdir
config
[
"
third_party
"
]
)
            
except
Exception
as
e
:
                
print
(
                    
"
Looks
like
config
.
yaml
is
not
valid
so
we
are
unable
"
                    
"
to
determine
default
checkers
and
which
folder
to
"
                    
"
exclude
using
defaults
provided
by
infer
"
                
)
                
print
(
e
)
        
return
checkers
tp_path
    
def
_get_infer_args
(
self
checks
third_party_path
)
:
        
"
"
"
Return
the
arguments
which
include
the
checkers
<
checks
>
and
        
excludes
all
folder
in
<
third_party_path
>
.
"
"
"
        
checkers
=
[
"
-
a
"
"
checkers
"
]
        
excludes
=
[
]
        
for
checker
in
checks
:
            
checkers
.
append
(
"
-
-
"
+
checker
)
        
with
open
(
third_party_path
)
as
f
:
            
for
line
in
f
:
                
excludes
.
append
(
"
-
-
skip
-
analysis
-
in
-
path
"
)
                
excludes
.
append
(
line
.
strip
(
"
\
n
"
)
)
        
return
checkers
excludes
    
def
_get_clang_tidy_config
(
self
)
:
        
try
:
            
file_handler
=
open
(
                
mozpath
.
join
(
self
.
topsrcdir
"
tools
"
"
clang
-
tidy
"
"
config
.
yaml
"
)
            
)
            
config
=
yaml
.
safe_load
(
file_handler
)
        
except
Exception
as
e
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
Looks
like
config
.
yaml
is
not
valid
we
are
going
to
use
default
"
                
"
values
for
the
rest
of
the
analysis
for
clang
-
tidy
.
"
            
)
            
print
(
e
)
            
return
None
        
return
config
    
def
_get_cov_config
(
self
)
:
        
try
:
            
file_handler
=
open
(
                
mozpath
.
join
(
self
.
topsrcdir
"
tools
"
"
coverity
"
"
config
.
yaml
"
)
            
)
            
config
=
yaml
.
safe_load
(
file_handler
)
        
except
Exception
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
Looks
like
config
.
yaml
is
not
valid
we
are
going
to
use
default
"
                
"
values
for
the
rest
of
the
analysis
for
coverity
.
"
            
)
            
return
None
        
return
config
    
def
_is_version_eligible
(
self
)
:
        
#
make
sure
that
we
'
ve
cached
self
.
_clang_tidy_config
        
if
self
.
_clang_tidy_config
is
None
:
            
self
.
_clang_tidy_config
=
self
.
_get_clang_tidy_config
(
)
        
version
=
None
        
if
"
package_version
"
in
self
.
_clang_tidy_config
:
            
version
=
self
.
_clang_tidy_config
[
"
package_version
"
]
        
else
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
Unable
to
find
'
package_version
'
in
the
config
.
yml
"
            
)
            
return
False
        
#
Because
the
fact
that
we
ship
together
clang
-
tidy
and
clang
-
format
        
#
we
are
sure
that
these
two
will
always
share
the
same
version
.
        
#
Thus
in
order
to
determine
that
the
version
is
compatible
we
only
        
#
need
to
check
one
of
them
going
with
clang
-
format
        
cmd
=
[
self
.
_clang_format_path
"
-
-
version
"
]
        
try
:
            
output
=
subprocess
.
check_output
(
cmd
stderr
=
subprocess
.
STDOUT
)
.
decode
(
                
"
utf
-
8
"
            
)
            
version_string
=
"
clang
-
format
version
"
+
version
            
if
output
.
startswith
(
version_string
)
:
                
return
True
        
except
subprocess
.
CalledProcessError
as
e
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
Error
determining
the
version
clang
-
tidy
/
format
binary
"
                
"
please
see
the
attached
exception
:
\
n
{
}
"
.
format
(
                    
e
.
output
                
)
            
)
        
return
False
    
def
_get_clang_tidy_command
(
self
checks
header_filter
sources
jobs
fix
)
:
        
if
checks
=
=
"
-
*
"
:
            
checks
=
self
.
_get_checks
(
)
        
common_args
=
[
            
"
-
clang
-
tidy
-
binary
"
            
self
.
_clang_tidy_path
            
"
-
clang
-
apply
-
replacements
-
binary
"
            
self
.
_clang_apply_replacements
            
"
-
checks
=
%
s
"
%
checks
            
"
-
extra
-
arg
=
-
DMOZ_CLANG_PLUGIN
"
        
]
        
#
Flag
header
-
filter
is
passed
in
order
to
limit
the
diagnostic
messages
only
        
#
to
the
specified
header
files
.
When
no
value
is
specified
the
default
value
        
#
is
considered
to
be
the
source
in
order
to
limit
the
diagnostic
message
to
        
#
the
source
files
or
folders
.
        
common_args
+
=
[
            
"
-
header
-
filter
=
%
s
"
            
%
(
header_filter
if
len
(
header_filter
)
else
"
|
"
.
join
(
sources
)
)
        
]
        
#
From
our
configuration
file
config
.
yaml
we
build
the
configuration
list
for
        
#
the
checkers
that
are
used
.
These
configuration
options
are
used
to
better
fit
        
#
the
checkers
to
our
code
.
        
cfg
=
self
.
_get_checks_config
(
)
        
if
cfg
:
            
common_args
+
=
[
"
-
config
=
%
s
"
%
yaml
.
dump
(
cfg
)
]
        
if
fix
:
            
common_args
+
=
[
"
-
fix
"
]
        
return
(
            
[
                
self
.
virtualenv_manager
.
python_path
                
self
.
_run_clang_tidy_path
                
"
-
j
"
                
str
(
jobs
)
                
"
-
p
"
                
self
.
_compilation_commands_path
            
]
            
+
common_args
            
+
sources
        
)
    
def
_check_for_java
(
self
)
:
        
"
"
"
Check
if
javac
can
be
found
.
"
"
"
        
import
distutils
        
java
=
self
.
substs
.
get
(
"
JAVA
"
)
        
java
=
java
or
os
.
getenv
(
"
JAVA_HOME
"
)
        
java
=
java
or
distutils
.
spawn
.
find_executable
(
"
javac
"
)
        
error
=
(
            
"
javac
was
not
found
!
Please
install
javac
and
either
add
it
to
your
PATH
"
        
)
        
error
+
=
"
set
JAVA_HOME
or
add
the
following
to
your
mozconfig
:
\
n
"
        
error
+
=
"
-
-
with
-
java
-
bin
-
path
=
/
path
/
to
/
java
/
bin
/
"
        
if
not
java
:
            
self
.
log
(
logging
.
ERROR
"
ERROR
:
static
-
analysis
"
{
}
error
)
            
return
1
        
return
0
    
def
_gradle
(
        
self
args
infer_args
=
None
verbose
=
False
autotest
=
False
suppress_output
=
True
    
)
:
        
infer_args
=
infer_args
or
[
]
        
if
autotest
:
            
cwd
=
mozpath
.
join
(
self
.
topsrcdir
"
tools
"
"
infer
"
"
test
"
)
            
gradle
=
mozpath
.
join
(
cwd
"
gradlew
"
)
        
else
:
            
gradle
=
self
.
substs
[
"
GRADLE
"
]
            
cwd
=
self
.
topsrcdir
        
extra_env
=
{
            
"
GRADLE_OPTS
"
:
"
-
Dfile
.
encoding
=
utf
-
8
"
#
see
mobile
/
android
/
mach_commands
.
py
            
"
JAVA_TOOL_OPTIONS
"
:
"
-
Dfile
.
encoding
=
utf
-
8
"
        
}
        
if
suppress_output
:
            
devnull
=
open
(
os
.
devnull
"
w
"
)
            
return
subprocess
.
call
(
                
infer_args
+
[
gradle
]
+
args
                
env
=
dict
(
os
.
environ
*
*
extra_env
)
                
cwd
=
cwd
                
stdout
=
devnull
                
stderr
=
subprocess
.
STDOUT
                
close_fds
=
True
            
)
        
return
self
.
run_process
(
            
infer_args
+
[
gradle
]
+
args
            
append_env
=
extra_env
            
pass_thru
=
True
#
Allow
user
to
run
gradle
interactively
.
            
ensure_exit_code
=
False
#
Don
'
t
throw
on
non
-
zero
exit
code
.
            
cwd
=
cwd
        
)
    
StaticAnalysisSubCommand
(
        
"
static
-
analysis
"
        
"
autotest
"
        
"
Run
the
auto
-
test
suite
in
order
to
determine
that
"
        
"
the
analysis
did
not
regress
.
"
    
)
    
CommandArgument
(
        
"
-
-
dump
-
results
"
        
"
-
d
"
        
default
=
False
        
action
=
"
store_true
"
        
help
=
"
Generate
the
baseline
for
the
regression
test
.
Based
on
"
        
"
this
baseline
we
will
test
future
results
.
"
    
)
    
CommandArgument
(
        
"
-
-
intree
-
tool
"
        
"
-
i
"
        
default
=
False
        
action
=
"
store_true
"
        
help
=
"
Use
a
pre
-
aquired
in
-
tree
clang
-
tidy
package
.
"
    
)
    
CommandArgument
(
        
"
checker_names
"
        
nargs
=
"
*
"
        
default
=
[
]
        
help
=
"
Checkers
that
are
going
to
be
auto
-
tested
.
"
    
)
    
def
autotest
(
        
self
verbose
=
False
dump_results
=
False
intree_tool
=
False
checker_names
=
[
]
    
)
:
        
#
If
'
dump_results
'
is
True
than
we
just
want
to
generate
the
issues
files
for
each
        
#
checker
in
particulat
and
thus
'
force_download
'
becomes
'
False
'
since
we
want
to
        
#
do
this
on
a
local
trusted
clang
-
tidy
package
.
        
self
.
_set_log_level
(
verbose
)
        
self
.
_dump_results
=
dump_results
        
force_download
=
not
self
.
_dump_results
        
#
Function
return
codes
        
self
.
TOOLS_SUCCESS
=
0
        
self
.
TOOLS_FAILED_DOWNLOAD
=
1
        
self
.
TOOLS_UNSUPORTED_PLATFORM
=
2
        
self
.
TOOLS_CHECKER_NO_TEST_FILE
=
3
        
self
.
TOOLS_CHECKER_RETURNED_NO_ISSUES
=
4
        
self
.
TOOLS_CHECKER_RESULT_FILE_NOT_FOUND
=
5
        
self
.
TOOLS_CHECKER_DIFF_FAILED
=
6
        
self
.
TOOLS_CHECKER_NOT_FOUND
=
7
        
self
.
TOOLS_CHECKER_FAILED_FILE
=
8
        
self
.
TOOLS_CHECKER_LIST_EMPTY
=
9
        
self
.
TOOLS_GRADLE_FAILED
=
10
        
#
Configure
the
tree
or
download
clang
-
tidy
package
depending
on
the
option
that
we
choose
        
if
intree_tool
:
            
_
config
_
=
self
.
_get_config_environment
(
)
            
clang_tools_path
=
self
.
topsrcdir
            
self
.
_clang_tidy_path
=
mozpath
.
join
(
                
clang_tools_path
                
"
clang
-
tidy
"
                
"
bin
"
                
"
clang
-
tidy
"
+
config
.
substs
.
get
(
"
BIN_SUFFIX
"
"
"
)
            
)
            
self
.
_clang_format_path
=
mozpath
.
join
(
                
clang_tools_path
                
"
clang
-
tidy
"
                
"
bin
"
                
"
clang
-
format
"
+
config
.
substs
.
get
(
"
BIN_SUFFIX
"
"
"
)
            
)
            
self
.
_clang_apply_replacements
=
mozpath
.
join
(
                
clang_tools_path
                
"
clang
-
tidy
"
                
"
bin
"
                
"
clang
-
apply
-
replacements
"
+
config
.
substs
.
get
(
"
BIN_SUFFIX
"
"
"
)
            
)
            
self
.
_run_clang_tidy_path
=
mozpath
.
join
(
                
clang_tools_path
"
clang
-
tidy
"
"
share
"
"
clang
"
"
run
-
clang
-
tidy
.
py
"
            
)
            
self
.
_clang_format_diff
=
mozpath
.
join
(
                
clang_tools_path
"
clang
-
tidy
"
"
share
"
"
clang
"
"
clang
-
format
-
diff
.
py
"
            
)
            
#
Ensure
that
clang
-
tidy
is
present
            
rc
=
not
os
.
path
.
exists
(
self
.
_clang_tidy_path
)
        
else
:
            
rc
=
self
.
_get_clang_tools
(
force
=
force_download
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
self
.
log
(
                
logging
.
ERROR
                
"
ERROR
:
static
-
analysis
"
                
{
}
                
"
clang
-
tidy
unable
to
locate
package
.
"
            
)
            
return
self
.
TOOLS_FAILED_DOWNLOAD
        
self
.
_clang_tidy_base_path
=
mozpath
.
join
(
self
.
topsrcdir
"
tools
"
"
clang
-
tidy
"
)
        
#
For
each
checker
run
it
        
self
.
_clang_tidy_config
=
self
.
_get_clang_tidy_config
(
)
        
platform
_
=
self
.
platform
        
if
platform
not
in
self
.
_clang_tidy_config
[
"
platforms
"
]
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
RUNNING
:
clang
-
tidy
autotest
for
platform
{
}
not
supported
.
"
.
format
(
                    
platform
                
)
            
)
            
return
self
.
TOOLS_UNSUPORTED_PLATFORM
        
import
concurrent
.
futures
        
import
multiprocessing
        
max_workers
=
multiprocessing
.
cpu_count
(
)
        
self
.
log
(
            
logging
.
INFO
            
"
static
-
analysis
"
            
{
}
            
"
RUNNING
:
clang
-
tidy
autotest
for
platform
{
0
}
with
{
1
}
workers
.
"
.
format
(
                
platform
max_workers
            
)
        
)
        
#
List
all
available
checkers
        
cmd
=
[
self
.
_clang_tidy_path
"
-
list
-
checks
"
"
-
checks
=
*
"
]
        
clang_output
=
subprocess
.
check_output
(
cmd
stderr
=
subprocess
.
STDOUT
)
.
decode
(
            
"
utf
-
8
"
        
)
        
available_checks
=
clang_output
.
split
(
"
\
n
"
)
[
1
:
]
        
self
.
_clang_tidy_checks
=
[
c
.
strip
(
)
for
c
in
available_checks
if
c
]
        
#
Build
the
dummy
compile_commands
.
json
        
self
.
_compilation_commands_path
=
self
.
_create_temp_compilation_db
(
            
self
.
_clang_tidy_config
        
)
        
checkers_test_batch
=
[
]
        
checkers_results
=
[
]
        
with
concurrent
.
futures
.
ThreadPoolExecutor
(
max_workers
=
max_workers
)
as
executor
:
            
futures
=
[
]
            
for
item
in
self
.
_clang_tidy_config
[
"
clang_checkers
"
]
:
                
#
Skip
if
any
of
the
following
statements
is
true
:
                
#
1
.
Checker
attribute
'
publish
'
is
False
.
                
not_published
=
not
bool
(
item
.
get
(
"
publish
"
True
)
)
                
#
2
.
Checker
has
restricted
-
platforms
and
current
platform
is
not
of
them
.
                
ignored_platform
=
(
                    
"
restricted
-
platforms
"
in
item
                    
and
platform
not
in
item
[
"
restricted
-
platforms
"
]
                
)
                
#
3
.
Checker
name
is
mozilla
-
*
or
-
*
.
                
ignored_checker
=
item
[
"
name
"
]
in
[
"
mozilla
-
*
"
"
-
*
"
]
                
#
4
.
List
checker_names
is
passed
and
the
current
checker
is
not
part
of
the
                
#
list
or
'
publish
'
is
False
                
checker_not_in_list
=
checker_names
and
(
                    
item
[
"
name
"
]
not
in
checker_names
or
not_published
                
)
                
if
(
                    
not_published
                    
or
ignored_platform
                    
or
ignored_checker
                    
or
checker_not_in_list
                
)
:
                    
continue
                
checkers_test_batch
.
append
(
item
[
"
name
"
]
)
                
futures
.
append
(
                    
executor
.
submit
(
self
.
_verify_checker
item
checkers_results
)
                
)
            
error_code
=
self
.
TOOLS_SUCCESS
            
for
future
in
concurrent
.
futures
.
as_completed
(
futures
)
:
                
#
Wait
for
every
task
to
finish
                
ret_val
=
future
.
result
(
)
                
if
ret_val
!
=
self
.
TOOLS_SUCCESS
:
                    
#
We
are
interested
only
in
one
error
and
we
don
'
t
break
                    
#
the
execution
of
for
loop
since
we
want
to
make
sure
that
all
                    
#
tasks
finished
.
                    
error_code
=
ret_val
            
if
error_code
!
=
self
.
TOOLS_SUCCESS
:
                
self
.
log
(
                    
logging
.
INFO
                    
"
static
-
analysis
"
                    
{
}
                    
"
FAIL
:
the
following
clang
-
tidy
check
(
s
)
failed
:
"
                
)
                
for
failure
in
checkers_results
:
                    
checker_error
=
failure
[
"
checker
-
error
"
]
                    
checker_name
=
failure
[
"
checker
-
name
"
]
                    
info1
=
failure
[
"
info1
"
]
                    
info2
=
failure
[
"
info2
"
]
                    
info3
=
failure
[
"
info3
"
]
                    
message_to_log
=
"
"
                    
if
checker_error
=
=
self
.
TOOLS_CHECKER_NOT_FOUND
:
                        
message_to_log
=
"
\
tChecker
{
}
not
present
in
this
"
                        
"
clang
-
tidy
version
.
"
.
format
(
                            
checker_name
                        
)
                    
elif
checker_error
=
=
self
.
TOOLS_CHECKER_NO_TEST_FILE
:
                        
message_to_log
=
"
\
tChecker
{
0
}
does
not
have
a
test
file
-
"
                        
"
{
0
}
.
cpp
"
.
format
(
                            
checker_name
                        
)
                    
elif
checker_error
=
=
self
.
TOOLS_CHECKER_RETURNED_NO_ISSUES
:
                        
message_to_log
=
"
\
tChecker
{
0
}
did
not
find
any
issues
in
its
"
                        
"
test
file
clang
-
tidy
output
for
the
run
is
:
\
n
{
1
}
"
.
format
(
                            
checker_name
info1
                        
)
                    
elif
checker_error
=
=
self
.
TOOLS_CHECKER_RESULT_FILE_NOT_FOUND
:
                        
message_to_log
=
"
\
tChecker
{
0
}
does
not
have
a
result
file
-
"
                        
"
{
0
}
.
json
"
.
format
(
                            
checker_name
                        
)
                    
elif
checker_error
=
=
self
.
TOOLS_CHECKER_DIFF_FAILED
:
                        
message_to_log
=
"
\
tChecker
{
0
}
\
nExpected
:
{
1
}
\
nGot
:
{
2
}
\
n
"
                        
"
clang
-
tidy
output
for
the
run
is
:
\
n
{
3
}
"
.
format
(
                            
checker_name
info1
info2
info3
                        
)
                    
print
(
"
\
n
"
+
message_to_log
)
                
#
Also
delete
the
tmp
folder
                
shutil
.
rmtree
(
self
.
_compilation_commands_path
)
                
return
error_code
            
#
Run
the
analysis
on
all
checkers
at
the
same
time
only
if
we
don
'
t
dump
results
.
            
if
not
self
.
_dump_results
:
                
ret_val
=
self
.
_run_analysis_batch
(
checkers_test_batch
)
                
if
ret_val
!
=
self
.
TOOLS_SUCCESS
:
                    
shutil
.
rmtree
(
self
.
_compilation_commands_path
)
                    
return
ret_val
        
self
.
log
(
            
logging
.
INFO
"
static
-
analysis
"
{
}
"
SUCCESS
:
clang
-
tidy
all
tests
passed
.
"
        
)
        
#
Also
delete
the
tmp
folder
        
shutil
.
rmtree
(
self
.
_compilation_commands_path
)
        
return
self
.
_autotest_infer
(
intree_tool
force_download
verbose
)
    
def
_run_analysis
(
        
self
checks
header_filter
sources
jobs
=
1
fix
=
False
print_out
=
False
    
)
:
        
cmd
=
self
.
_get_clang_tidy_command
(
            
checks
=
checks
            
header_filter
=
header_filter
            
sources
=
sources
            
jobs
=
jobs
            
fix
=
fix
        
)
        
try
:
            
clang_output
=
subprocess
.
check_output
(
                
cmd
stderr
=
subprocess
.
STDOUT
            
)
.
decode
(
"
utf
-
8
"
)
        
except
subprocess
.
CalledProcessError
as
e
:
            
print
(
e
.
output
)
            
return
None
        
return
self
.
_parse_issues
(
clang_output
)
clang_output
    
def
_run_analysis_batch
(
self
items
)
:
        
self
.
log
(
            
logging
.
INFO
            
"
static
-
analysis
"
            
{
}
            
"
RUNNING
:
clang
-
tidy
checker
batch
analysis
.
"
        
)
        
if
not
len
(
items
)
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
ERROR
:
clang
-
tidy
checker
list
is
empty
!
"
            
)
            
return
self
.
TOOLS_CHECKER_LIST_EMPTY
        
issues
clang_output
=
self
.
_run_analysis
(
            
checks
=
"
-
*
"
+
"
"
.
join
(
items
)
            
header_filter
=
"
"
            
sources
=
[
                
mozpath
.
join
(
self
.
_clang_tidy_base_path
"
test
"
checker
)
+
"
.
cpp
"
                
for
checker
in
items
            
]
            
print_out
=
True
        
)
        
if
issues
is
None
:
            
return
self
.
TOOLS_CHECKER_FAILED_FILE
        
failed_checks
=
[
]
        
failed_checks_baseline
=
[
]
        
for
checker
in
items
:
            
test_file_path_json
=
(
                
mozpath
.
join
(
self
.
_clang_tidy_base_path
"
test
"
checker
)
+
"
.
json
"
            
)
            
#
Read
the
pre
-
determined
issues
            
baseline_issues
=
self
.
_get_autotest_stored_issues
(
test_file_path_json
)
            
#
We
also
stored
the
'
reliability
'
index
so
strip
that
from
the
baseline_issues
            
baseline_issues
[
:
]
=
[
                
item
for
item
in
baseline_issues
if
"
reliability
"
not
in
item
            
]
            
found
=
all
(
[
element_base
in
issues
for
element_base
in
baseline_issues
]
)
            
if
not
found
:
                
failed_checks
.
append
(
checker
)
                
failed_checks_baseline
.
append
(
baseline_issues
)
        
if
len
(
failed_checks
)
>
0
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
The
following
check
(
s
)
failed
for
bulk
analysis
:
"
                
+
"
"
.
join
(
failed_checks
)
            
)
            
for
failed_check
baseline_issue
in
zip
(
                
failed_checks
failed_checks_baseline
            
)
:
                
print
(
                    
"
\
tChecker
{
0
}
expect
following
results
:
\
n
\
t
\
t
{
1
}
"
.
format
(
                        
failed_check
baseline_issue
                    
)
                
)
            
print
(
                
"
This
is
the
output
generated
by
clang
-
tidy
for
the
bulk
build
:
\
n
{
}
"
.
format
(
                    
clang_output
                
)
            
)
            
return
self
.
TOOLS_CHECKER_DIFF_FAILED
        
return
self
.
TOOLS_SUCCESS
    
def
_create_temp_compilation_db
(
self
config
)
:
        
directory
=
tempfile
.
mkdtemp
(
prefix
=
"
cc
"
)
        
with
open
(
            
mozpath
.
join
(
directory
"
compile_commands
.
json
"
)
"
wb
"
        
)
as
file_handler
:
            
compile_commands
=
[
]
            
director
=
mozpath
.
join
(
self
.
topsrcdir
"
tools
"
"
clang
-
tidy
"
"
test
"
)
            
for
item
in
config
[
"
clang_checkers
"
]
:
                
if
item
[
"
name
"
]
in
[
"
-
*
"
"
mozilla
-
*
"
]
:
                    
continue
                
file
=
item
[
"
name
"
]
+
"
.
cpp
"
                
element
=
{
}
                
element
[
"
directory
"
]
=
director
                
element
[
"
command
"
]
=
"
cpp
"
+
file
                
element
[
"
file
"
]
=
mozpath
.
join
(
director
file
)
                
compile_commands
.
append
(
element
)
            
json
.
dump
(
compile_commands
file_handler
)
            
file_handler
.
flush
(
)
            
return
directory
    
def
_autotest_infer
(
self
intree_tool
force_download
verbose
)
:
        
#
infer
is
not
available
on
other
platforms
but
autotest
should
work
even
without
        
#
it
being
installed
        
if
self
.
platform
[
0
]
=
=
"
linux64
"
:
            
rc
=
self
.
_check_for_java
(
)
            
if
rc
!
=
0
:
                
return
1
            
rc
=
self
.
_get_infer
(
                
force
=
force_download
verbose
=
verbose
intree_tool
=
intree_tool
            
)
            
if
rc
!
=
0
:
                
self
.
log
(
                    
logging
.
ERROR
                    
"
ERROR
:
static
-
analysis
"
                    
{
}
                    
"
infer
unable
to
locate
package
.
"
                
)
                
return
self
.
TOOLS_FAILED_DOWNLOAD
            
self
.
__infer_tool
=
mozpath
.
join
(
self
.
topsrcdir
"
tools
"
"
infer
"
)
            
self
.
__infer_test_folder
=
mozpath
.
join
(
self
.
__infer_tool
"
test
"
)
            
import
concurrent
.
futures
            
import
multiprocessing
            
max_workers
=
multiprocessing
.
cpu_count
(
)
            
self
.
log
(
                
logging
.
INFO
                
"
static
-
analysis
"
                
{
}
                
"
RUNNING
:
infer
autotest
for
platform
{
0
}
with
{
1
}
workers
.
"
.
format
(
                    
self
.
platform
[
0
]
max_workers
                
)
            
)
            
#
clean
previous
autotest
if
it
exists
            
rc
=
self
.
_gradle
(
[
"
autotest
:
clean
"
]
autotest
=
True
)
            
if
rc
!
=
0
:
                
return
rc
            
import
yaml
            
with
open
(
mozpath
.
join
(
self
.
__infer_tool
"
config
.
yaml
"
)
)
as
f
:
                
config
=
yaml
.
safe_load
(
f
)
            
with
concurrent
.
futures
.
ThreadPoolExecutor
(
                
max_workers
=
max_workers
            
)
as
executor
:
                
futures
=
[
]
                
for
item
in
config
[
"
infer_checkers
"
]
:
                    
if
item
[
"
publish
"
]
:
                        
futures
.
append
(
                            
executor
.
submit
(
self
.
_verify_infer_checker
item
)
                        
)
                
#
this
is
always
included
in
check
-
java
but
not
in
config
.
yaml
                
futures
.
append
(
                    
executor
.
submit
(
self
.
_verify_infer_checker
{
"
name
"
:
"
checkers
"
}
)
                
)
                
for
future
in
concurrent
.
futures
.
as_completed
(
futures
)
:
                    
ret_val
=
future
.
result
(
)
                    
if
ret_val
!
=
self
.
TOOLS_SUCCESS
:
                        
return
ret_val
            
self
.
log
(
                
logging
.
INFO
"
static
-
analysis
"
{
}
"
SUCCESS
:
infer
all
tests
passed
.
"
            
)
        
else
:
            
self
.
log
(
                
logging
.
WARNING
                
"
static
-
analysis
"
                
{
}
                
"
Skipping
infer
autotest
because
it
is
only
available
on
linux64
!
"
            
)
        
return
self
.
TOOLS_SUCCESS
    
def
_verify_infer_checker
(
self
item
)
:
        
"
"
"
Given
a
checker
this
method
verifies
the
following
:
          
1
.
if
there
is
a
checker
.
json
and
checker
.
java
file
in
             
tools
/
infer
/
test
/
autotest
/
src
          
2
.
if
running
infer
on
checker
.
java
yields
the
same
result
as
checker
.
json
        
An
item
is
simply
a
dictionary
which
needs
to
have
a
name
field
set
which
is
the
        
name
of
the
checker
.
        
"
"
"
        
def
to_camelcase
(
str
)
:
            
return
"
"
.
join
(
[
s
.
capitalize
(
)
for
s
in
str
.
split
(
"
-
"
)
]
)
        
check
=
item
[
"
name
"
]
        
test_file_path
=
mozpath
.
join
(
            
self
.
__infer_tool
            
"
test
"
            
"
autotest
"
            
"
src
"
            
"
main
"
            
"
java
"
            
to_camelcase
(
check
)
        
)
        
test_file_path_java
=
test_file_path
+
"
.
java
"
        
test_file_path_json
=
test_file_path
+
"
.
json
"
        
self
.
log
(
            
logging
.
INFO
            
"
static
-
analysis
"
            
{
}
            
"
RUNNING
:
infer
check
{
}
.
"
.
format
(
check
)
        
)
        
#
Verify
if
the
test
file
exists
for
this
checker
        
if
not
os
.
path
.
exists
(
test_file_path_java
)
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
ERROR
:
infer
check
{
}
doesn
'
t
have
a
test
file
.
"
.
format
(
check
)
            
)
            
return
self
.
TOOLS_CHECKER_NO_TEST_FILE
        
#
run
infer
on
a
particular
test
file
        
out_folder
=
mozpath
.
join
(
            
self
.
__infer_test_folder
"
test
-
infer
-
{
}
"
.
format
(
check
)
        
)
        
if
check
=
=
"
checkers
"
:
            
check_arg
=
[
"
-
a
"
"
checkers
"
]
        
else
:
            
check_arg
=
[
"
-
-
{
}
-
only
"
.
format
(
check
)
]
        
infer_args
=
[
self
.
_infer_path
"
run
"
]
+
check_arg
+
[
"
-
o
"
out_folder
"
-
-
"
]
        
gradle_args
=
[
"
autotest
:
compileInferTest
{
}
"
.
format
(
to_camelcase
(
check
)
)
]
        
rc
=
self
.
_gradle
(
gradle_args
infer_args
=
infer_args
autotest
=
True
)
        
if
rc
!
=
0
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
ERROR
:
infer
failed
to
execute
gradle
{
}
.
"
.
format
(
gradle_args
)
            
)
            
return
self
.
TOOLS_GRADLE_FAILED
        
issues
=
json
.
load
(
open
(
mozpath
.
join
(
out_folder
"
report
.
json
"
)
)
)
        
#
remove
folder
that
infer
creates
because
the
issues
are
loaded
into
memory
        
shutil
.
rmtree
(
out_folder
)
        
#
Verify
to
see
if
we
got
any
issues
if
not
raise
exception
        
if
not
issues
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
ERROR
:
infer
check
{
0
}
did
not
find
any
issues
in
its
"
                
"
associated
test
suite
.
"
.
format
(
                    
check
                
)
            
)
            
return
self
.
TOOLS_CHECKER_RETURNED_NO_ISSUES
        
if
self
.
_dump_results
:
            
self
.
_build_autotest_result
(
test_file_path_json
issues
)
        
else
:
            
if
not
os
.
path
.
exists
(
test_file_path_json
)
:
                
#
Result
file
for
test
not
found
maybe
regenerate
it
?
                
self
.
log
(
                    
logging
.
ERROR
                    
"
static
-
analysis
"
                    
{
}
                    
"
ERROR
:
infer
result
file
not
found
for
check
{
0
}
"
.
format
(
check
)
                
)
                
return
self
.
TOOLS_CHECKER_RESULT_FILE_NOT_FOUND
            
#
Read
the
pre
-
determined
issues
            
baseline_issues
=
self
.
_get_autotest_stored_issues
(
test_file_path_json
)
            
def
ordered
(
obj
)
:
                
if
isinstance
(
obj
dict
)
:
                    
return
sorted
(
(
k
ordered
(
v
)
)
for
k
v
in
obj
.
items
(
)
)
                
if
isinstance
(
obj
list
)
:
                    
return
sorted
(
ordered
(
x
)
for
x
in
obj
)
                
return
obj
            
#
Compare
the
two
lists
            
if
ordered
(
issues
)
!
=
ordered
(
baseline_issues
)
:
                
error_str
=
"
ERROR
:
in
check
{
}
Expected
:
"
.
format
(
check
)
                
error_str
+
=
"
\
n
"
+
json
.
dumps
(
baseline_issues
indent
=
2
)
                
error_str
+
=
"
\
n
Got
:
\
n
"
+
json
.
dumps
(
issues
indent
=
2
)
                
self
.
log
(
                    
logging
.
ERROR
                    
"
static
-
analysis
"
                    
{
}
                    
"
ERROR
:
infer
autotest
for
check
{
}
failed
check
stdout
for
"
                    
"
more
details
"
.
format
(
                        
check
                    
)
                
)
                
print
(
error_str
)
                
return
self
.
TOOLS_CHECKER_DIFF_FAILED
        
return
self
.
TOOLS_SUCCESS
    
StaticAnalysisSubCommand
(
        
"
static
-
analysis
"
"
install
"
"
Install
the
static
analysis
helper
tool
"
    
)
    
CommandArgument
(
        
"
source
"
        
nargs
=
"
?
"
        
type
=
str
        
help
=
"
Where
to
fetch
a
local
archive
containing
the
static
-
analysis
and
"
        
"
format
helper
tool
.
"
        
"
It
will
be
installed
in
~
/
.
mozbuild
/
clang
-
tools
and
~
/
.
mozbuild
/
infer
.
"
        
"
Can
be
omitted
in
which
case
the
latest
clang
-
tools
and
infer
"
        
"
helper
for
the
platform
would
be
automatically
detected
and
installed
.
"
    
)
    
CommandArgument
(
        
"
-
-
skip
-
cache
"
        
action
=
"
store_true
"
        
help
=
"
Skip
all
local
caches
to
force
re
-
fetching
the
helper
tool
.
"
        
default
=
False
    
)
    
CommandArgument
(
        
"
-
-
force
"
        
action
=
"
store_true
"
        
help
=
"
Force
re
-
install
even
though
the
tool
exists
in
mozbuild
.
"
        
default
=
False
    
)
    
CommandArgument
(
        
"
-
-
minimal
-
install
"
        
action
=
"
store_true
"
        
help
=
"
Download
only
clang
based
tool
.
"
        
default
=
False
    
)
    
def
install
(
        
self
        
source
=
None
        
skip_cache
=
False
        
force
=
False
        
minimal_install
=
False
        
verbose
=
False
    
)
:
        
self
.
_set_log_level
(
verbose
)
        
rc
=
self
.
_get_clang_tools
(
            
force
=
force
skip_cache
=
skip_cache
source
=
source
verbose
=
verbose
        
)
        
if
rc
=
=
0
and
not
minimal_install
:
            
#
XXX
ignore
the
return
code
because
if
it
fails
or
not
infer
is
            
#
not
mandatory
but
clang
-
tidy
is
            
self
.
_get_infer
(
force
=
force
skip_cache
=
skip_cache
verbose
=
verbose
)
        
return
rc
    
StaticAnalysisSubCommand
(
        
"
static
-
analysis
"
        
"
clear
-
cache
"
        
"
Delete
local
helpers
and
reset
static
analysis
helper
tool
cache
"
    
)
    
def
clear_cache
(
self
verbose
=
False
)
:
        
self
.
_set_log_level
(
verbose
)
        
rc
=
self
.
_get_clang_tools
(
            
force
=
True
download_if_needed
=
True
skip_cache
=
True
verbose
=
verbose
        
)
        
if
rc
=
=
0
:
            
self
.
_get_infer
(
                
force
=
True
download_if_needed
=
True
skip_cache
=
True
verbose
=
verbose
            
)
        
if
rc
!
=
0
:
            
return
rc
        
return
self
.
_artifact_manager
.
artifact_clear_cache
(
)
    
StaticAnalysisSubCommand
(
        
"
static
-
analysis
"
        
"
print
-
checks
"
        
"
Print
a
list
of
the
static
analysis
checks
performed
by
default
"
    
)
    
def
print_checks
(
self
verbose
=
False
)
:
        
self
.
_set_log_level
(
verbose
)
        
rc
=
self
.
_get_clang_tools
(
verbose
=
verbose
)
        
if
rc
=
=
0
:
            
rc
=
self
.
_get_infer
(
verbose
=
verbose
)
        
if
rc
!
=
0
:
            
return
rc
        
args
=
[
            
self
.
_clang_tidy_path
            
"
-
list
-
checks
"
            
"
-
checks
=
%
s
"
%
self
.
_get_checks
(
)
        
]
        
rc
=
self
.
_run_command_in_objdir
(
args
=
args
pass_thru
=
True
)
        
if
rc
!
=
0
:
            
return
rc
        
checkers
_
=
self
.
_get_infer_config
(
)
        
print
(
"
Infer
checks
:
"
)
        
for
checker
in
checkers
:
            
print
(
"
"
*
4
+
checker
)
        
return
0
    
Command
(
        
"
clang
-
format
"
        
category
=
"
misc
"
        
description
=
"
Run
clang
-
format
on
current
changes
"
    
)
    
CommandArgument
(
        
"
-
-
show
"
        
"
-
s
"
        
action
=
"
store_const
"
        
const
=
"
stdout
"
        
dest
=
"
output_path
"
        
help
=
"
Show
diff
output
on
stdout
instead
of
applying
changes
"
    
)
    
CommandArgument
(
        
"
-
-
assume
-
filename
"
        
"
-
a
"
        
nargs
=
1
        
default
=
None
        
help
=
"
This
option
is
usually
used
in
the
context
of
hg
-
formatsource
.
"
        
"
When
reading
from
stdin
clang
-
format
assumes
this
"
        
"
filename
to
look
for
a
style
config
file
(
with
"
        
"
-
style
=
file
)
and
to
determine
the
language
.
When
"
        
"
specifying
this
option
only
one
file
should
be
used
"
        
"
as
an
input
and
the
output
will
be
forwarded
to
stdin
.
"
        
"
This
option
also
impairs
the
download
of
the
clang
-
tools
"
        
"
and
assumes
the
package
is
already
located
in
it
'
s
default
"
        
"
location
"
    
)
    
CommandArgument
(
        
"
-
-
path
"
"
-
p
"
nargs
=
"
+
"
default
=
None
help
=
"
Specify
the
path
(
s
)
to
reformat
"
    
)
    
CommandArgument
(
        
"
-
-
commit
"
        
"
-
c
"
        
default
=
None
        
help
=
"
Specify
a
commit
to
reformat
from
.
"
        
"
For
git
you
can
also
pass
a
range
of
commits
(
foo
.
.
bar
)
"
        
"
to
format
all
of
them
at
the
same
time
.
"
    
)
    
CommandArgument
(
        
"
-
-
output
"
        
"
-
o
"
        
default
=
None
        
dest
=
"
output_path
"
        
help
=
"
Specify
a
file
handle
to
write
clang
-
format
raw
output
instead
of
"
        
"
applying
changes
.
This
can
be
stdout
or
a
file
path
.
"
    
)
    
CommandArgument
(
        
"
-
-
format
"
        
"
-
f
"
        
choices
=
(
"
diff
"
"
json
"
)
        
default
=
"
diff
"
        
dest
=
"
output_format
"
        
help
=
"
Specify
the
output
format
used
:
diff
is
the
raw
patch
provided
by
"
        
"
clang
-
format
json
is
a
list
of
atomic
changes
to
process
.
"
    
)
    
CommandArgument
(
        
"
-
-
outgoing
"
        
default
=
False
        
action
=
"
store_true
"
        
help
=
"
Run
clang
-
format
on
outgoing
files
from
mercurial
repository
"
    
)
    
def
clang_format
(
        
self
        
assume_filename
        
path
        
commit
        
output_path
=
None
        
output_format
=
"
diff
"
        
verbose
=
False
        
outgoing
=
False
    
)
:
        
#
Run
clang
-
format
or
clang
-
format
-
diff
on
the
local
changes
        
#
or
files
/
directories
        
if
path
is
None
and
outgoing
:
            
repo
=
get_repository_object
(
self
.
topsrcdir
)
            
path
=
repo
.
get_outgoing_files
(
)
        
if
path
:
            
#
Create
the
full
path
list
            
def
path_maker
(
f_name
)
:
return
os
.
path
.
join
(
self
.
topsrcdir
f_name
)
            
path
=
map
(
path_maker
path
)
        
os
.
chdir
(
self
.
topsrcdir
)
        
#
Load
output
file
handle
either
stdout
or
a
file
handle
in
write
mode
        
output
=
None
        
if
output_path
is
not
None
:
            
output
=
sys
.
stdout
if
output_path
=
=
"
stdout
"
else
open
(
output_path
"
w
"
)
        
#
With
assume_filename
we
want
to
have
stdout
clean
since
the
result
of
the
        
#
format
will
be
redirected
to
stdout
.
Only
in
case
of
error
we
        
#
write
something
to
stdout
.
        
#
We
don
'
t
actually
want
to
get
the
clang
-
tools
here
since
we
want
in
some
        
#
scenarios
to
do
this
in
parallel
so
we
relay
on
the
fact
that
the
tools
        
#
have
already
been
downloaded
via
'
.
/
mach
bootstrap
'
or
directly
via
        
#
'
.
/
mach
static
-
analysis
install
'
        
if
assume_filename
:
            
rc
=
self
.
_set_clang_tools_paths
(
)
            
if
rc
!
=
0
:
                
print
(
"
clang
-
format
:
Unable
to
set
path
to
clang
-
format
tools
.
"
)
                
return
rc
            
if
not
self
.
_do_clang_tools_exist
(
)
:
                
print
(
"
clang
-
format
:
Unable
to
set
locate
clang
-
format
tools
.
"
)
                
return
1
        
else
:
            
rc
=
self
.
_get_clang_tools
(
verbose
=
verbose
)
            
if
rc
!
=
0
:
                
return
rc
        
if
self
.
_is_version_eligible
(
)
is
False
:
            
self
.
log
(
                
logging
.
ERROR
                
"
static
-
analysis
"
                
{
}
                
"
You
'
re
using
an
old
version
of
clang
-
format
binary
.
"
                
"
Please
update
to
a
more
recent
one
by
running
:
'
.
/
mach
bootstrap
'
"
            
)
            
return
1
        
if
path
is
None
:
            
return
self
.
_run_clang_format_diff
(
                
self
.
_clang_format_diff
self
.
_clang_format_path
commit
output
            
)
        
if
assume_filename
:
            
return
self
.
_run_clang_format_in_console
(
                
self
.
_clang_format_path
path
assume_filename
            
)
        
return
self
.
_run_clang_format_path
(
            
self
.
_clang_format_path
path
output
output_format
        
)
    
def
_verify_checker
(
self
item
checkers_results
)
:
        
check
=
item
[
"
name
"
]
        
test_file_path
=
mozpath
.
join
(
self
.
_clang_tidy_base_path
"
test
"
check
)
        
test_file_path_cpp
=
test_file_path
+
"
.
cpp
"
        
test_file_path_json
=
test_file_path
+
"
.
json
"
        
self
.
log
(
            
logging
.
INFO
            
"
static
-
analysis
"
            
{
}
            
"
RUNNING
:
clang
-
tidy
checker
{
}
.
"
.
format
(
check
)
        
)
        
#
Structured
information
in
case
a
checker
fails
        
checker_error
=
{
            
"
checker
-
name
"
:
check
            
"
checker
-
error
"
:
"
"
            
"
info1
"
:
"
"
            
"
info2
"
:
"
"
            
"
info3
"
:
"
"
        
}
        
#
Verify
if
this
checker
actually
exists
        
if
check
not
in
self
.
_clang_tidy_checks
:
            
checker_error
[
"
checker
-
error
"
]
=
self
.
TOOLS_CHECKER_NOT_FOUND
            
checkers_results
.
append
(
checker_error
)
            
return
self
.
TOOLS_CHECKER_NOT_FOUND
        
#
Verify
if
the
test
file
exists
for
this
checker
        
if
not
os
.
path
.
exists
(
test_file_path_cpp
)
:
            
checker_error
[
"
checker
-
error
"
]
=
self
.
TOOLS_CHECKER_NO_TEST_FILE
            
checkers_results
.
append
(
checker_error
)
            
return
self
.
TOOLS_CHECKER_NO_TEST_FILE
        
issues
clang_output
=
self
.
_run_analysis
(
            
checks
=
"
-
*
"
+
check
header_filter
=
"
"
sources
=
[
test_file_path_cpp
]
        
)
        
if
issues
is
None
:
            
return
self
.
TOOLS_CHECKER_FAILED_FILE
        
#
Verify
to
see
if
we
got
any
issues
if
not
raise
exception
        
if
not
issues
:
            
checker_error
[
"
checker
-
error
"
]
=
self
.
TOOLS_CHECKER_RETURNED_NO_ISSUES
            
checker_error
[
"
info1
"
]
=
clang_output
            
checkers_results
.
append
(
checker_error
)
            
return
self
.
TOOLS_CHECKER_RETURNED_NO_ISSUES
        
#
Also
store
the
'
reliability
'
index
for
this
checker
        
issues
.
append
(
{
"
reliability
"
:
item
[
"
reliability
"
]
}
)
        
if
self
.
_dump_results
:
            
self
.
_build_autotest_result
(
test_file_path_json
json
.
dumps
(
issues
)
)
        
else
:
            
if
not
os
.
path
.
exists
(
test_file_path_json
)
:
                
#
Result
file
for
test
not
found
maybe
regenerate
it
?
                
checker_error
[
                    
"
checker
-
error
"
                
]
=
self
.
TOOLS_CHECKER_RESULT_FILE_NOT_FOUND
                
checkers_results
.
append
(
checker_error
)
                
return
self
.
TOOLS_CHECKER_RESULT_FILE_NOT_FOUND
            
#
Read
the
pre
-
determined
issues
            
baseline_issues
=
self
.
_get_autotest_stored_issues
(
test_file_path_json
)
            
#
Compare
the
two
lists
            
if
issues
!
=
baseline_issues
:
                
checker_error
[
"
checker
-
error
"
]
=
self
.
TOOLS_CHECKER_DIFF_FAILED
                
checker_error
[
"
info1
"
]
=
baseline_issues
                
checker_error
[
"
info2
"
]
=
issues
                
checker_error
[
"
info3
"
]
=
clang_output
                
checkers_results
.
append
(
checker_error
)
                
return
self
.
TOOLS_CHECKER_DIFF_FAILED
        
return
self
.
TOOLS_SUCCESS
    
def
_build_autotest_result
(
self
file
issues
)
:
        
with
open
(
file
"
w
"
)
as
f
:
            
f
.
write
(
issues
)
    
def
_get_autotest_stored_issues
(
self
file
)
:
        
with
open
(
file
)
as
f
:
            
return
json
.
load
(
f
)
    
def
_parse_issues
(
self
clang_output
)
:
        
"
"
"
        
Parse
clang
-
tidy
output
into
structured
issues
        
"
"
"
        
#
Limit
clang
output
parsing
to
'
Enabled
checks
:
'
        
end
=
re
.
search
(
r
"
^
Enabled
checks
:
\
n
"
clang_output
re
.
MULTILINE
)
        
if
end
is
not
None
:
            
clang_output
=
clang_output
[
:
end
.
start
(
)
-
1
]
        
platform
_
=
self
.
platform
        
#
Starting
with
clang
8
for
the
diagnostic
messages
we
have
multiple
LF
CR
        
#
in
order
to
be
compatible
with
msvc
compiler
format
and
for
this
        
#
we
are
not
interested
to
match
the
end
of
line
.
        
regex_string
=
(
            
r
"
(
.
+
)
:
(
\
d
+
)
:
(
\
d
+
)
:
(
warning
|
error
)
:
(
[
^
\
[
\
]
\
n
]
+
)
(
?
:
\
[
(
[
\
.
\
w
-
]
+
)
\
]
)
"
        
)
        
#
For
non
'
win
'
based
platforms
we
also
need
the
'
end
of
the
line
'
regex
        
if
platform
not
in
(
"
win64
"
"
win32
"
)
:
            
regex_string
+
=
"
?
"
        
regex_header
=
re
.
compile
(
regex_string
re
.
MULTILINE
)
        
#
Sort
headers
by
positions
        
headers
=
sorted
(
regex_header
.
finditer
(
clang_output
)
key
=
lambda
h
:
h
.
start
(
)
)
        
issues
=
[
]
        
for
_
header
in
enumerate
(
headers
)
:
            
header_group
=
header
.
groups
(
)
            
element
=
[
header_group
[
3
]
header_group
[
4
]
header_group
[
5
]
]
            
issues
.
append
(
element
)
        
return
issues
    
def
_get_checks
(
self
)
:
        
checks
=
"
-
*
"
        
try
:
            
config
=
self
.
_clang_tidy_config
            
for
item
in
config
[
"
clang_checkers
"
]
:
                
if
item
.
get
(
"
publish
"
True
)
:
                    
checks
+
=
"
"
+
item
[
"
name
"
]
        
except
Exception
:
            
print
(
                
"
Looks
like
config
.
yaml
is
not
valid
so
we
are
unable
to
"
                
"
determine
default
checkers
using
'
-
checks
=
-
*
mozilla
-
*
'
"
            
)
            
checks
+
=
"
mozilla
-
*
"
        
finally
:
            
return
checks
    
def
_get_checks_config
(
self
)
:
        
config_list
=
[
]
        
checker_config
=
{
}
        
try
:
            
config
=
self
.
_clang_tidy_config
            
for
checker
in
config
[
"
clang_checkers
"
]
:
                
if
checker
.
get
(
"
publish
"
True
)
and
"
config
"
in
checker
:
                    
for
checker_option
in
checker
[
"
config
"
]
:
                        
#
Verify
if
the
format
of
the
Option
is
correct
                        
#
possibilities
are
:
                        
#
1
.
CheckerName
.
Option
                        
#
2
.
Option
-
>
that
will
become
CheckerName
.
Option
                        
if
not
checker_option
[
"
key
"
]
.
startswith
(
checker
[
"
name
"
]
)
:
                            
checker_option
[
"
key
"
]
=
"
{
}
.
{
}
"
.
format
(
                                
checker
[
"
name
"
]
checker_option
[
"
key
"
]
                            
)
                    
config_list
+
=
checker
[
"
config
"
]
            
checker_config
[
"
CheckOptions
"
]
=
config_list
        
except
Exception
:
            
print
(
                
"
Looks
like
config
.
yaml
is
not
valid
so
we
are
unable
to
"
                
"
determine
configuration
for
checkers
so
using
default
"
            
)
            
checker_config
=
None
        
finally
:
            
return
checker_config
    
def
_get_config_environment
(
self
)
:
        
ran_configure
=
False
        
config
=
None
        
builder
=
Build
(
self
.
_mach_context
)
        
try
:
            
config
=
self
.
config_environment
        
except
Exception
:
            
print
(
"
Looks
like
configure
has
not
run
yet
running
it
now
.
.
.
"
)
            
rc
=
builder
.
configure
(
)
            
if
rc
!
=
0
:
                
return
(
rc
config
ran_configure
)
            
ran_configure
=
True
            
try
:
                
config
=
self
.
config_environment
            
except
Exception
:
                
pass
        
return
(
0
config
ran_configure
)
    
def
_build_compile_db
(
self
verbose
=
False
)
:
        
self
.
_compile_db
=
mozpath
.
join
(
self
.
topobjdir
"
compile_commands
.
json
"
)
        
if
os
.
path
.
exists
(
self
.
_compile_db
)
:
            
return
0
        
rc
config
ran_configure
=
self
.
_get_config_environment
(
)
        
if
rc
!
=
0
:
            
return
rc
        
if
ran_configure
:
            
#
Configure
may
have
created
the
compilation
database
if
the
            
#
mozconfig
enables
building
the
CompileDB
backend
by
default
            
#
So
we
recurse
to
see
if
the
file
exists
once
again
.
            
return
self
.
_build_compile_db
(
verbose
=
verbose
)
        
if
config
:
            
print
(
                
"
Looks
like
a
clang
compilation
database
has
not
been
"
                
"
created
yet
creating
it
now
.
.
.
"
            
)
            
builder
=
Build
(
self
.
_mach_context
)
            
rc
=
builder
.
build_backend
(
[
"
CompileDB
"
]
verbose
=
verbose
)
            
if
rc
!
=
0
:
                
return
rc
            
assert
os
.
path
.
exists
(
self
.
_compile_db
)
            
return
0
    
def
_build_export
(
self
jobs
verbose
=
False
)
:
        
def
on_line
(
line
)
:
            
self
.
log
(
logging
.
INFO
"
build_output
"
{
"
line
"
:
line
}
"
{
line
}
"
)
        
builder
=
Build
(
self
.
_mach_context
)
        
#
First
install
what
we
can
through
install
manifests
.
        
rc
=
builder
.
_run_make
(
            
directory
=
self
.
topobjdir
            
target
=
"
pre
-
export
"
            
line_handler
=
None
            
silent
=
not
verbose
        
)
        
if
rc
!
=
0
:
            
return
rc
        
#
Then
build
the
rest
of
the
build
dependencies
by
running
the
full
        
#
export
target
because
we
can
'
t
do
anything
better
.
        
return
builder
.
_run_make
(
            
directory
=
self
.
topobjdir
            
target
=
"
export
"
            
line_handler
=
None
            
silent
=
not
verbose
            
num_jobs
=
jobs
        
)
    
def
_set_clang_tools_paths
(
self
)
:
        
rc
config
_
=
self
.
_get_config_environment
(
)
        
if
rc
!
=
0
:
            
return
rc
        
self
.
_clang_tools_path
=
mozpath
.
join
(
            
self
.
_mach_context
.
state_dir
"
clang
-
tools
"
        
)
        
self
.
_clang_tidy_path
=
mozpath
.
join
(
            
self
.
_clang_tools_path
            
"
clang
-
tidy
"
            
"
bin
"
            
"
clang
-
tidy
"
+
config
.
substs
.
get
(
"
BIN_SUFFIX
"
"
"
)
        
)
        
self
.
_clang_format_path
=
mozpath
.
join
(
            
self
.
_clang_tools_path
            
"
clang
-
tidy
"
            
"
bin
"
            
"
clang
-
format
"
+
config
.
substs
.
get
(
"
BIN_SUFFIX
"
"
"
)
        
)
        
self
.
_clang_apply_replacements
=
mozpath
.
join
(
            
self
.
_clang_tools_path
            
"
clang
-
tidy
"
            
"
bin
"
            
"
clang
-
apply
-
replacements
"
+
config
.
substs
.
get
(
"
BIN_SUFFIX
"
"
"
)
        
)
        
self
.
_run_clang_tidy_path
=
mozpath
.
join
(
            
self
.
_clang_tools_path
"
clang
-
tidy
"
"
share
"
"
clang
"
"
run
-
clang
-
tidy
.
py
"
        
)
        
self
.
_clang_format_diff
=
mozpath
.
join
(
            
self
.
_clang_tools_path
            
"
clang
-
tidy
"
            
"
share
"
            
"
clang
"
            
"
clang
-
format
-
diff
.
py
"
        
)
        
return
0
    
def
_do_clang_tools_exist
(
self
)
:
        
return
(
            
os
.
path
.
exists
(
self
.
_clang_tidy_path
)
            
and
os
.
path
.
exists
(
self
.
_clang_format_path
)
            
and
os
.
path
.
exists
(
self
.
_clang_apply_replacements
)
            
and
os
.
path
.
exists
(
self
.
_run_clang_tidy_path
)
        
)
    
def
_get_clang_tools
(
        
self
        
force
=
False
        
skip_cache
=
False
        
source
=
None
        
download_if_needed
=
True
        
verbose
=
False
    
)
:
        
rc
=
self
.
_set_clang_tools_paths
(
)
        
if
rc
!
=
0
:
            
return
rc
        
if
self
.
_do_clang_tools_exist
(
)
and
not
force
:
            
return
0
        
if
os
.
path
.
isdir
(
self
.
_clang_tools_path
)
and
download_if_needed
:
            
#
The
directory
exists
perhaps
it
'
s
corrupted
?
Delete
it
            
#
and
start
from
scratch
.
            
shutil
.
rmtree
(
self
.
_clang_tools_path
)
            
return
self
.
_get_clang_tools
(
                
force
=
force
                
skip_cache
=
skip_cache
                
source
=
source
                
verbose
=
verbose
                
download_if_needed
=
download_if_needed
            
)
        
#
Create
base
directory
where
we
store
clang
binary
        
os
.
mkdir
(
self
.
_clang_tools_path
)
        
if
source
:
            
return
self
.
_get_clang_tools_from_source
(
source
)
        
self
.
_artifact_manager
=
PackageFrontend
(
self
.
_mach_context
)
        
if
not
download_if_needed
:
            
return
0
        
job
_
=
self
.
platform
        
if
job
is
None
:
            
raise
Exception
(
                
"
The
current
platform
isn
'
t
supported
.
"
                
"
Currently
only
the
following
platforms
are
"
                
"
supported
:
win32
/
win64
linux64
and
macosx64
.
"
            
)
        
job
+
=
"
-
clang
-
tidy
"
        
#
We
want
to
unpack
data
in
the
clang
-
tidy
mozbuild
folder
        
currentWorkingDir
=
os
.
getcwd
(
)
        
os
.
chdir
(
self
.
_clang_tools_path
)
        
rc
=
self
.
_artifact_manager
.
artifact_toolchain
(
            
verbose
=
verbose
            
skip_cache
=
skip_cache
            
from_build
=
[
job
]
            
no_unpack
=
False
            
retry
=
0
        
)
        
#
Change
back
the
cwd
        
os
.
chdir
(
currentWorkingDir
)
        
return
rc
    
def
_get_clang_tools_from_source
(
self
filename
)
:
        
from
mozbuild
.
action
.
tooltool
import
unpack_file
        
clang_tidy_path
=
mozpath
.
join
(
self
.
_mach_context
.
state_dir
"
clang
-
tools
"
)
        
currentWorkingDir
=
os
.
getcwd
(
)
        
os
.
chdir
(
clang_tidy_path
)
        
unpack_file
(
filename
)
        
#
Change
back
the
cwd
        
os
.
chdir
(
currentWorkingDir
)
        
clang_path
=
mozpath
.
join
(
clang_tidy_path
"
clang
"
)
        
if
not
os
.
path
.
isdir
(
clang_path
)
:
            
raise
Exception
(
                
"
Extracted
the
archive
but
didn
'
t
find
"
"
the
expected
output
"
            
)
        
assert
os
.
path
.
exists
(
self
.
_clang_tidy_path
)
        
assert
os
.
path
.
exists
(
self
.
_clang_format_path
)
        
assert
os
.
path
.
exists
(
self
.
_clang_apply_replacements
)
        
assert
os
.
path
.
exists
(
self
.
_run_clang_tidy_path
)
        
return
0
    
def
_get_clang_format_diff_command
(
self
commit
)
:
        
if
self
.
repository
.
name
=
=
"
hg
"
:
            
args
=
[
"
hg
"
"
diff
"
"
-
U0
"
]
            
if
commit
:
                
args
+
=
[
"
-
c
"
commit
]
            
else
:
                
args
+
=
[
"
-
r
"
"
.
^
"
]
            
for
dot_extension
in
self
.
_format_include_extensions
:
                
args
+
=
[
"
-
-
include
"
"
glob
:
*
*
{
0
}
"
.
format
(
dot_extension
)
]
            
args
+
=
[
"
-
-
exclude
"
"
listfile
:
{
0
}
"
.
format
(
self
.
_format_ignore_file
)
]
        
else
:
            
commit_range
=
"
HEAD
"
#
All
uncommitted
changes
.
            
if
commit
:
                
commit_range
=
(
                    
commit
if
"
.
.
"
in
commit
else
"
{
}
~
.
.
{
}
"
.
format
(
commit
commit
)
                
)
            
args
=
[
"
git
"
"
diff
"
"
-
-
no
-
color
"
"
-
U0
"
commit_range
"
-
-
"
]
            
for
dot_extension
in
self
.
_format_include_extensions
:
                
args
+
=
[
"
*
{
0
}
"
.
format
(
dot_extension
)
]
            
#
git
-
diff
doesn
'
t
support
an
'
exclude
-
from
-
files
'
param
but
            
#
allow
to
add
individual
exclude
pattern
since
v1
.
9
see
            
#
https
:
/
/
git
-
scm
.
com
/
docs
/
gitglossary
#
gitglossary
-
aiddefpathspecapathspec
            
with
open
(
self
.
_format_ignore_file
"
rb
"
)
as
exclude_pattern_file
:
                
for
pattern
in
exclude_pattern_file
.
readlines
(
)
:
                    
pattern
=
pattern
.
rstrip
(
)
                    
pattern
=
pattern
.
replace
(
"
.
*
"
"
*
*
"
)
                    
if
not
pattern
or
pattern
.
startswith
(
"
#
"
)
:
                        
continue
#
empty
or
comment
                    
magics
=
[
"
exclude
"
]
                    
if
pattern
.
startswith
(
"
^
"
)
:
                        
magics
+
=
[
"
top
"
]
                        
pattern
=
pattern
[
1
:
]
                    
args
+
=
[
"
:
(
{
0
}
)
{
1
}
"
.
format
(
"
"
.
join
(
magics
)
pattern
)
]
        
return
args
    
def
_get_infer
(
        
self
        
force
=
False
        
skip_cache
=
False
        
download_if_needed
=
True
        
verbose
=
False
        
intree_tool
=
False
    
)
:
        
rc
config
_
=
self
.
_get_config_environment
(
)
        
if
rc
!
=
0
:
            
return
rc
        
infer_path
=
(
            
self
.
topsrcdir
            
if
intree_tool
            
else
mozpath
.
join
(
self
.
_mach_context
.
state_dir
"
infer
"
)
        
)
        
self
.
_infer_path
=
mozpath
.
join
(
            
infer_path
"
infer
"
"
bin
"
"
infer
"
+
config
.
substs
.
get
(
"
BIN_SUFFIX
"
"
"
)
        
)
        
if
intree_tool
:
            
return
not
os
.
path
.
exists
(
self
.
_infer_path
)
        
if
os
.
path
.
exists
(
self
.
_infer_path
)
and
not
force
:
            
return
0
        
if
os
.
path
.
isdir
(
infer_path
)
and
download_if_needed
:
            
#
The
directory
exists
perhaps
it
'
s
corrupted
?
Delete
it
            
#
and
start
from
scratch
.
            
shutil
.
rmtree
(
infer_path
)
            
return
self
.
_get_infer
(
                
force
=
force
                
skip_cache
=
skip_cache
                
verbose
=
verbose
                
download_if_needed
=
download_if_needed
            
)
        
os
.
mkdir
(
infer_path
)
        
self
.
_artifact_manager
=
PackageFrontend
(
self
.
_mach_context
)
        
if
not
download_if_needed
:
            
return
0
        
job
_
=
self
.
platform
        
if
job
!
=
"
linux64
"
:
            
return
-
1
        
else
:
            
job
+
=
"
-
infer
"
        
#
We
want
to
unpack
data
in
the
infer
mozbuild
folder
        
currentWorkingDir
=
os
.
getcwd
(
)
        
os
.
chdir
(
infer_path
)
        
rc
=
self
.
_artifact_manager
.
artifact_toolchain
(
            
verbose
=
verbose
            
skip_cache
=
skip_cache
            
from_build
=
[
job
]
            
no_unpack
=
False
            
retry
=
0
        
)
        
#
Change
back
the
cwd
        
os
.
chdir
(
currentWorkingDir
)
        
return
rc
    
def
_run_clang_format_diff
(
        
self
clang_format_diff
clang_format
commit
output_file
    
)
:
        
#
Run
clang
-
format
on
the
diff
        
#
Note
that
this
will
potentially
miss
a
lot
things
        
from
subprocess
import
Popen
PIPE
check_output
CalledProcessError
        
diff_process
=
Popen
(
self
.
_get_clang_format_diff_command
(
commit
)
stdout
=
PIPE
)
        
args
=
[
sys
.
executable
clang_format_diff
"
-
p1
"
"
-
binary
=
%
s
"
%
clang_format
]
        
if
not
output_file
:
            
args
.
append
(
"
-
i
"
)
        
try
:
            
output
=
check_output
(
args
stdin
=
diff_process
.
stdout
)
            
if
output_file
:
                
#
We
want
to
print
the
diffs
                
print
(
output
file
=
output_file
)
            
return
0
        
except
CalledProcessError
as
e
:
            
#
Something
wrong
happened
            
print
(
"
clang
-
format
:
An
error
occurred
while
running
clang
-
format
-
diff
.
"
)
            
return
e
.
returncode
    
def
_is_ignored_path
(
self
ignored_dir_re
f
)
:
        
#
Remove
up
to
topsrcdir
in
pathname
and
match
        
if
f
.
startswith
(
self
.
topsrcdir
+
"
/
"
)
:
            
match_f
=
f
[
len
(
self
.
topsrcdir
+
"
/
"
)
:
]
        
else
:
            
match_f
=
f
        
return
re
.
match
(
ignored_dir_re
match_f
)
    
def
_generate_path_list
(
self
paths
verbose
=
True
)
:
        
path_to_third_party
=
os
.
path
.
join
(
self
.
topsrcdir
self
.
_format_ignore_file
)
        
ignored_dir
=
[
]
        
with
open
(
path_to_third_party
"
r
"
)
as
fh
:
            
for
line
in
fh
:
                
#
Remove
comments
and
empty
lines
                
if
line
.
startswith
(
"
#
"
)
or
len
(
line
.
strip
(
)
)
=
=
0
:
                    
continue
                
#
The
regexp
is
to
make
sure
we
are
managing
relative
paths
                
ignored_dir
.
append
(
r
"
^
[
\
.
/
]
*
"
+
line
.
rstrip
(
)
)
        
#
Generates
the
list
of
regexp
        
ignored_dir_re
=
"
(
%
s
)
"
%
"
|
"
.
join
(
ignored_dir
)
        
extensions
=
self
.
_format_include_extensions
        
path_list
=
[
]
        
for
f
in
paths
:
            
if
self
.
_is_ignored_path
(
ignored_dir_re
f
)
:
                
#
Early
exit
if
we
have
provided
an
ignored
directory
                
if
verbose
:
                    
print
(
"
clang
-
format
:
Ignored
third
party
code
'
{
0
}
'
"
.
format
(
f
)
)
                
continue
            
if
os
.
path
.
isdir
(
f
)
:
                
#
Processing
a
directory
generate
the
file
list
                
for
folder
subs
files
in
os
.
walk
(
f
)
:
                    
subs
.
sort
(
)
                    
for
filename
in
sorted
(
files
)
:
                        
f_in_dir
=
os
.
path
.
join
(
folder
filename
)
                        
if
f_in_dir
.
endswith
(
extensions
)
and
not
self
.
_is_ignored_path
(
                            
ignored_dir_re
f_in_dir
                        
)
:
                            
#
Supported
extension
and
accepted
path
                            
path_list
.
append
(
f_in_dir
)
            
else
:
                
#
Make
sure
that
the
file
exists
and
it
has
a
supported
extension
                
if
os
.
path
.
isfile
(
f
)
and
f
.
endswith
(
extensions
)
:
                    
path_list
.
append
(
f
)
        
return
path_list
    
def
_run_clang_format_in_console
(
self
clang_format
paths
assume_filename
)
:
        
path_list
=
self
.
_generate_path_list
(
assume_filename
False
)
        
if
path_list
=
=
[
]
:
            
return
0
        
#
We
use
-
assume
-
filename
in
order
to
better
determine
the
path
for
        
#
the
.
clang
-
format
when
it
is
ran
outside
of
the
repo
for
example
        
#
by
the
extension
hg
-
formatsource
        
args
=
[
clang_format
"
-
assume
-
filename
=
{
}
"
.
format
(
assume_filename
[
0
]
)
]
        
process
=
subprocess
.
Popen
(
args
stdin
=
subprocess
.
PIPE
)
        
with
open
(
paths
[
0
]
"
r
"
)
as
fin
:
            
process
.
stdin
.
write
(
fin
.
read
(
)
)
            
process
.
stdin
.
close
(
)
            
process
.
wait
(
)
            
return
process
.
returncode
    
def
_run_clang_format_path
(
self
clang_format
paths
output_file
output_format
)
:
        
#
Run
clang
-
format
on
files
or
directories
directly
        
from
subprocess
import
check_output
CalledProcessError
        
if
output_format
=
=
"
json
"
:
            
#
Get
replacements
in
xml
then
process
to
json
            
args
=
[
clang_format
"
-
output
-
replacements
-
xml
"
]
        
else
:
            
args
=
[
clang_format
"
-
i
"
]
        
if
output_file
:
            
#
We
just
want
to
show
the
diff
we
create
the
directory
to
copy
it
            
tmpdir
=
os
.
path
.
join
(
self
.
topobjdir
"
tmp
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
tmpdir
)
:
                
os
.
makedirs
(
tmpdir
)
        
path_list
=
self
.
_generate_path_list
(
paths
)
        
if
path_list
=
=
[
]
:
            
return
        
print
(
"
Processing
%
d
file
(
s
)
.
.
.
"
%
len
(
path_list
)
)
        
if
output_file
:
            
patches
=
{
}
            
for
i
in
range
(
0
len
(
path_list
)
)
:
                
l
=
path_list
[
i
:
(
i
+
1
)
]
                
#
Copy
the
files
into
a
temp
directory
                
#
and
run
clang
-
format
on
the
temp
directory
                
#
and
show
the
diff
                
original_path
=
l
[
0
]
                
local_path
=
ntpath
.
basename
(
original_path
)
                
target_file
=
os
.
path
.
join
(
tmpdir
local_path
)
                
faketmpdir
=
os
.
path
.
dirname
(
target_file
)
                
if
not
os
.
path
.
isdir
(
faketmpdir
)
:
                    
os
.
makedirs
(
faketmpdir
)
                
shutil
.
copy
(
l
[
0
]
faketmpdir
)
                
l
[
0
]
=
target_file
                
#
Run
clang
-
format
on
the
list
                
try
:
                    
output
=
check_output
(
args
+
l
)
                    
if
output
and
output_format
=
=
"
json
"
:
                        
patches
[
original_path
]
=
self
.
_parse_xml_output
(
                            
original_path
output
                        
)
                
except
CalledProcessError
as
e
:
                    
#
Something
wrong
happened
                    
print
(
"
clang
-
format
:
An
error
occurred
while
running
clang
-
format
.
"
)
                    
return
e
.
returncode
                
#
show
the
diff
                
if
output_format
=
=
"
diff
"
:
                    
diff_command
=
[
"
diff
"
"
-
u
"
original_path
target_file
]
                    
try
:
                        
output
=
check_output
(
diff_command
)
                    
except
CalledProcessError
as
e
:
                        
#
diff
-
u
returns
0
when
no
change
                        
#
here
we
expect
changes
.
if
we
are
here
this
means
that
                        
#
there
is
a
diff
to
show
                        
if
e
.
output
:
                            
#
Replace
the
temp
path
by
the
path
relative
to
the
repository
                            
#
to
display
a
valid
patch
                            
relative_path
=
os
.
path
.
relpath
(
                                
original_path
self
.
topsrcdir
                            
)
                            
patch
=
e
.
output
.
replace
(
target_file
relative_path
)
                            
patch
=
patch
.
replace
(
original_path
relative_path
)
                            
patches
[
original_path
]
=
patch
            
if
output_format
=
=
"
json
"
:
                
output
=
json
.
dumps
(
patches
indent
=
4
)
            
else
:
                
#
Display
all
the
patches
at
once
                
output
=
"
\
n
"
.
join
(
patches
.
values
(
)
)
            
#
Output
to
specified
file
or
stdout
            
print
(
output
file
=
output_file
)
            
shutil
.
rmtree
(
tmpdir
)
            
return
0
        
#
Run
clang
-
format
in
parallel
trying
to
saturate
all
of
the
available
cores
.
        
import
concurrent
.
futures
        
import
multiprocessing
        
import
math
        
max_workers
=
multiprocessing
.
cpu_count
(
)
        
#
To
maximize
CPU
usage
when
there
are
few
items
to
handle
        
#
underestimate
the
number
of
items
per
batch
then
dispatch
        
#
outstanding
items
across
workers
.
Per
definition
each
worker
will
        
#
handle
at
most
one
outstanding
item
.
        
batch_size
=
int
(
math
.
floor
(
float
(
len
(
path_list
)
)
/
max_workers
)
)
        
outstanding_items
=
len
(
path_list
)
-
batch_size
*
max_workers
        
batches
=
[
]
        
i
=
0
        
while
i
<
len
(
path_list
)
:
            
num_items
=
batch_size
+
(
1
if
outstanding_items
>
0
else
0
)
            
batches
.
append
(
args
+
path_list
[
i
:
(
i
+
num_items
)
]
)
            
outstanding_items
-
=
1
            
i
+
=
num_items
        
error_code
=
None
        
with
concurrent
.
futures
.
ThreadPoolExecutor
(
max_workers
=
max_workers
)
as
executor
:
            
futures
=
[
]
            
for
batch
in
batches
:
                
futures
.
append
(
executor
.
submit
(
run_one_clang_format_batch
batch
)
)
            
for
future
in
concurrent
.
futures
.
as_completed
(
futures
)
:
                
#
Wait
for
every
task
to
finish
                
ret_val
=
future
.
result
(
)
                
if
ret_val
is
not
None
:
                    
error_code
=
ret_val
            
if
error_code
is
not
None
:
                
return
error_code
        
return
0
    
def
_parse_xml_output
(
self
path
clang_output
)
:
        
"
"
"
        
Parse
the
clang
-
format
XML
output
to
convert
it
in
a
JSON
compatible
        
list
of
patches
and
calculates
line
level
information
from
the
        
character
level
provided
changes
.
        
"
"
"
        
content
=
open
(
path
"
r
"
)
.
read
(
)
.
decode
(
"
utf
-
8
"
)
        
def
_nb_of_lines
(
start
end
)
:
            
return
len
(
content
[
start
:
end
]
.
splitlines
(
)
)
        
def
_build
(
replacement
)
:
            
offset
=
int
(
replacement
.
attrib
[
"
offset
"
]
)
            
length
=
int
(
replacement
.
attrib
[
"
length
"
]
)
            
last_line
=
content
.
rfind
(
"
\
n
"
0
offset
)
            
return
{
                
"
replacement
"
:
replacement
.
text
                
"
char_offset
"
:
offset
                
"
char_length
"
:
length
                
"
line
"
:
_nb_of_lines
(
0
offset
)
                
"
line_offset
"
:
last_line
!
=
-
1
and
(
offset
-
last_line
)
or
0
                
"
lines_modified
"
:
_nb_of_lines
(
offset
offset
+
length
)
            
}
        
return
[
            
_build
(
replacement
)
            
for
replacement
in
ET
.
fromstring
(
clang_output
)
.
findall
(
"
replacement
"
)
        
]
