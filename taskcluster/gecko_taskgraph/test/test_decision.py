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
tempfile
from
unittest
.
mock
import
MagicMock
patch
import
pytest
from
mozunit
import
MockedOpen
main
from
taskgraph
.
util
import
json
from
taskgraph
.
util
.
yaml
import
load_yaml
from
gecko_taskgraph
import
decision
from
gecko_taskgraph
.
parameters
import
register_parameters
FAKE_GRAPH_CONFIG
=
{
"
product
-
dir
"
:
"
browser
"
"
taskgraph
"
:
{
}
}
TTC_FILE
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
"
try_task_config
.
json
"
)
pytest
.
fixture
(
scope
=
"
module
"
autouse
=
True
)
def
register
(
)
:
    
register_parameters
(
)
pytest
.
fixture
(
scope
=
"
module
"
)
def
options
(
)
:
    
return
{
        
"
base_repository
"
:
"
https
:
/
/
hg
.
mozilla
.
org
/
mozilla
-
unified
"
        
"
base_ref
"
:
"
mybranch
"
        
"
base_rev
"
:
"
1234
"
        
"
head_repository
"
:
"
https
:
/
/
hg
.
mozilla
.
org
/
mozilla
-
central
"
        
"
head_rev
"
:
"
abcd
"
        
"
head_ref
"
:
"
ef01
"
        
"
head_tag
"
:
"
"
        
"
message
"
:
"
"
        
"
project
"
:
"
mozilla
-
central
"
        
"
pushlog_id
"
:
"
143
"
        
"
pushdate
"
:
1503691511
        
"
owner
"
:
"
nobody
mozilla
.
com
"
        
"
repository_type
"
:
"
hg
"
        
"
tasks_for
"
:
"
hg
-
push
"
        
"
level
"
:
"
3
"
    
}
def
test_write_artifact_json
(
)
:
    
data
=
[
{
"
some
"
:
"
data
"
}
]
    
tmpdir
=
tempfile
.
mkdtemp
(
)
    
try
:
        
decision
.
ARTIFACTS_DIR
=
os
.
path
.
join
(
tmpdir
"
artifacts
"
)
        
decision
.
write_artifact
(
"
artifact
.
json
"
data
)
        
with
open
(
os
.
path
.
join
(
decision
.
ARTIFACTS_DIR
"
artifact
.
json
"
)
)
as
f
:
            
assert
json
.
load
(
f
)
=
=
data
    
finally
:
        
if
os
.
path
.
exists
(
tmpdir
)
:
            
shutil
.
rmtree
(
tmpdir
)
        
decision
.
ARTIFACTS_DIR
=
"
artifacts
"
def
test_write_artifact_yml
(
)
:
    
data
=
[
{
"
some
"
:
"
data
"
}
]
    
tmpdir
=
tempfile
.
mkdtemp
(
)
    
try
:
        
decision
.
ARTIFACTS_DIR
=
os
.
path
.
join
(
tmpdir
"
artifacts
"
)
        
decision
.
write_artifact
(
"
artifact
.
yml
"
data
)
        
assert
load_yaml
(
decision
.
ARTIFACTS_DIR
"
artifact
.
yml
"
)
=
=
data
    
finally
:
        
if
os
.
path
.
exists
(
tmpdir
)
:
            
shutil
.
rmtree
(
tmpdir
)
        
decision
.
ARTIFACTS_DIR
=
"
artifacts
"
patch
(
"
gecko_taskgraph
.
decision
.
get_hg_revision_info
"
)
patch
(
"
gecko_taskgraph
.
decision
.
get_hg_revision_branch
"
)
patch
(
"
gecko_taskgraph
.
decision
.
get_repository
"
)
patch
(
"
gecko_taskgraph
.
decision
.
get_changed_files
"
)
pytest
.
mark
.
parametrize
(
    
"
extra_options
commit_msg
ttc
expected
"
    
(
        
pytest
.
param
(
            
{
}
            
None
            
None
            
{
                
"
pushlog_id
"
:
"
143
"
                
"
build_date
"
:
1503691511
                
"
files_changed
"
:
[
"
bar
/
baz
.
md
"
"
foo
.
txt
"
]
                
"
hg_branch
"
:
"
default
"
                
"
moz_build_date
"
:
"
20170825200511
"
                
"
try_mode
"
:
None
                
"
try_task_config
"
:
{
}
                
"
head_git_rev
"
:
"
bcde
"
            
}
            
id
=
"
simple_options
"
        
)
        
pytest
.
param
(
            
{
"
owner
"
:
"
ffxbld
"
}
            
None
            
None
            
{
                
"
owner
"
:
"
ffxbld
noreply
.
mozilla
.
org
"
            
}
            
id
=
"
no_email_owner
"
        
)
        
pytest
.
param
(
            
{
"
project
"
:
"
try
"
}
            
"
try
:
-
b
do
-
t
all
-
-
artifact
"
            
None
            
{
                
"
try_mode
"
:
None
                
"
try_task_config
"
:
{
}
                
"
head_git_rev
"
:
"
bcde
"
            
}
            
id
=
"
try_options
"
        
)
        
pytest
.
param
(
            
{
                
"
project
"
:
"
try
"
            
}
            
"
Fuzzy
query
=
foo
"
            
{
"
tasks
"
:
[
"
a
"
"
b
"
]
}
            
{
                
"
try_mode
"
:
"
try_task_config
"
                
"
try_task_config
"
:
{
"
tasks
"
:
[
"
a
"
"
b
"
]
}
                
"
head_git_rev
"
:
"
bcde
"
            
}
            
id
=
"
try_task_config
"
        
)
    
)
)
def
test_get_decision_parameters
(
    
mock_get_changed_files
    
mock_get_repository
    
mock_get_hg_revision_branch
    
mock_get_hg_revision_info
    
options
    
extra_options
    
commit_msg
    
ttc
    
expected
)
:
    
mock_get_hg_revision_info
.
return_value
=
"
bcde
"
    
mock_get_hg_revision_branch
.
return_value
=
"
default
"
    
mock_repo
=
MagicMock
(
)
    
mock_repo
.
default_branch
=
"
baseref
"
    
mock_repo
.
get_commit_message
.
return_value
=
commit_msg
or
"
commit
message
"
    
mock_get_repository
.
return_value
=
mock_repo
    
mock_get_changed_files
.
return_value
=
[
"
foo
.
txt
"
"
bar
/
baz
.
md
"
]
    
options
.
update
(
extra_options
)
    
contents
=
None
    
if
ttc
:
        
contents
=
json
.
dumps
(
ttc
)
    
with
MockedOpen
(
{
TTC_FILE
:
contents
}
)
:
        
params
=
decision
.
get_decision_parameters
(
FAKE_GRAPH_CONFIG
options
)
    
for
key
in
expected
:
        
assert
params
[
key
]
=
=
expected
[
key
]
f
"
key
{
key
}
does
not
match
!
"
pytest
.
mark
.
parametrize
(
    
"
msg
expected
"
    
(
        
pytest
.
param
(
"
"
"
"
id
=
"
empty
"
)
        
pytest
.
param
(
"
abc
|
def
"
"
"
id
=
"
no_try_syntax
"
)
        
pytest
.
param
(
"
try
:
-
f
-
o
-
o
"
"
try
:
-
f
-
o
-
o
"
id
=
"
initial_try_syntax
"
)
        
pytest
.
param
(
            
"
some
stuff
\
ntry
:
-
f
-
o
-
o
\
nabc
\
ndef
"
            
"
try
:
-
f
-
o
-
o
"
            
id
=
"
embedded_try_syntax_multiline
"
        
)
    
)
)
def
test_try_syntax_from_message
(
msg
expected
)
:
    
assert
decision
.
try_syntax_from_message
(
msg
)
=
=
expected
if
__name__
=
=
"
__main__
"
:
    
main
(
)
