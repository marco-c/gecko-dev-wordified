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
"
"
"
Transform
the
partner
attribution
task
into
an
actual
task
description
.
"
"
"
import
json
import
logging
from
collections
import
defaultdict
from
taskgraph
.
transforms
.
base
import
TransformSequence
from
gecko_taskgraph
.
util
.
partners
import
(
    
apply_partner_priority
    
build_macos_attribution_dmg_command
    
check_if_partners_enabled
    
generate_attribution_code
    
get_ftp_platform
    
get_partner_config_by_kind
)
log
=
logging
.
getLogger
(
__name__
)
transforms
=
TransformSequence
(
)
transforms
.
add
(
check_if_partners_enabled
)
transforms
.
add
(
apply_partner_priority
)
transforms
.
add
def
add_command_arguments
(
config
tasks
)
:
    
enabled_partners
=
config
.
params
.
get
(
"
release_partners
"
)
    
attribution_config
=
get_partner_config_by_kind
(
config
config
.
kind
)
    
for
task
in
tasks
:
        
dependencies
=
{
}
        
fetches
=
defaultdict
(
set
)
        
attributions
=
[
]
        
release_artifacts
=
[
]
        
task_platforms
=
task
.
pop
(
"
platforms
"
[
]
)
        
for
partner_config
in
attribution_config
.
get
(
"
configs
"
[
]
)
:
            
#
we
might
only
be
interested
in
a
subset
of
all
partners
eg
for
a
respin
            
if
enabled_partners
and
partner_config
[
"
campaign
"
]
not
in
enabled_partners
:
                
continue
            
attribution_code
=
generate_attribution_code
(
                
attribution_config
[
"
defaults
"
]
partner_config
            
)
            
for
platform
in
partner_config
[
"
platforms
"
]
:
                
if
platform
not
in
task_platforms
:
                    
continue
                
stage_platform
=
platform
.
replace
(
"
-
shippable
"
"
"
)
                
for
locale
in
partner_config
[
"
locales
"
]
:
                    
upstream_label
upstream_artifact
=
(
                        
_get_upstream_task_label_and_artifact
(
platform
locale
)
                    
)
                    
if
upstream_label
not
in
config
.
kind_dependencies_tasks
:
                        
raise
Exception
(
                            
f
"
Can
'
t
find
upstream
task
for
{
platform
}
{
locale
}
"
                        
)
                    
upstream
=
config
.
kind_dependencies_tasks
[
upstream_label
]
                    
#
set
the
dependencies
to
just
what
we
need
rather
than
all
of
l10n
                    
dependencies
.
update
(
{
upstream
.
label
:
upstream
.
label
}
)
                    
fetches
[
upstream_label
]
.
add
(
                        
(
upstream_artifact
stage_platform
locale
)
                    
)
                    
output_artifact
=
_get_output_path
(
partner_config
platform
locale
)
                    
#
config
for
script
                    
#
TODO
-
generalise
input
&
output
?
?
                    
#
add
releng
/
partner
prefix
via
get_artifact_prefix
.
.
(
)
                    
attributions
.
append
(
                        
{
                            
"
input
"
:
_get_input_path
(
stage_platform
platform
locale
)
                            
"
output
"
:
"
/
builds
/
worker
/
artifacts
/
{
}
"
.
format
(
                                
output_artifact
                            
)
                            
"
attribution
"
:
attribution_code
                        
}
                    
)
                    
release_artifacts
.
append
(
output_artifact
)
        
if
attributions
:
            
worker
=
task
.
get
(
"
worker
"
{
}
)
            
worker
[
"
chain
-
of
-
trust
"
]
=
True
            
task
.
setdefault
(
"
dependencies
"
{
}
)
.
update
(
dependencies
)
            
task
.
setdefault
(
"
fetches
"
{
}
)
            
for
upstream_label
upstream_artifacts
in
fetches
.
items
(
)
:
                
task
[
"
fetches
"
]
[
upstream_label
]
=
[
                    
{
                        
"
artifact
"
:
upstream_artifact
                        
"
dest
"
:
"
{
platform
}
/
{
locale
}
"
.
format
(
                            
platform
=
platform
locale
=
locale
                        
)
                        
"
extract
"
:
False
                        
"
verify
-
hash
"
:
True
                    
}
                    
for
upstream_artifact
platform
locale
in
upstream_artifacts
                
]
            
worker
[
"
artifacts
"
]
=
[
                
{
                    
"
name
"
:
"
releng
/
partner
"
                    
"
path
"
:
"
/
builds
/
worker
/
artifacts
/
releng
/
partner
"
                    
"
type
"
:
"
directory
"
                
}
            
]
            
task
.
setdefault
(
"
attributes
"
{
}
)
[
"
release_artifacts
"
]
=
release_artifacts
            
_build_attribution_config
(
task
task_platforms
attributions
)
            
yield
task
def
_get_input_path
(
stage_platform
platform
locale
)
:
    
return
(
        
"
/
builds
/
worker
/
fetches
/
{
stage_platform
}
/
{
locale
}
/
{
artifact_file_name
}
"
.
format
(
            
stage_platform
=
stage_platform
            
locale
=
locale
            
artifact_file_name
=
_get_artifact_file_name
(
platform
)
        
)
    
)
def
_get_output_path
(
partner_config
platform
locale
)
:
    
return
"
releng
/
partner
/
{
partner
}
/
{
sub_partner
}
/
{
ftp_platform
}
/
{
locale
}
/
{
artifact_file_name
}
"
.
format
(
        
partner
=
partner_config
[
"
campaign
"
]
        
sub_partner
=
partner_config
[
"
content
"
]
        
ftp_platform
=
get_ftp_platform
(
platform
)
        
locale
=
locale
        
artifact_file_name
=
_get_artifact_file_name
(
platform
)
    
)
def
_get_artifact_file_name
(
platform
)
:
    
if
platform
.
startswith
(
"
win
"
)
:
        
return
"
target
.
installer
.
exe
"
    
elif
platform
.
startswith
(
"
macos
"
)
:
        
return
"
target
.
dmg
"
    
else
:
        
raise
NotImplementedError
(
            
'
Case
for
platform
"
{
}
"
is
not
implemented
'
.
format
(
platform
)
        
)
def
_get_upstream_task_label_and_artifact
(
platform
locale
)
:
    
#
find
the
upstream
throw
away
locales
we
don
'
t
have
somehow
.
Skip
?
    
if
platform
.
startswith
(
"
win
"
)
:
        
if
locale
=
=
"
en
-
US
"
:
            
upstream_label
=
"
repackage
-
signing
-
{
platform
}
/
opt
"
.
format
(
                
platform
=
platform
            
)
            
upstream_artifact
=
"
target
.
installer
.
exe
"
        
else
:
            
upstream_label
=
"
repackage
-
signing
-
l10n
-
{
locale
}
-
{
platform
}
/
opt
"
.
format
(
                
locale
=
locale
platform
=
platform
            
)
            
upstream_artifact
=
"
{
locale
}
/
target
.
installer
.
exe
"
.
format
(
locale
=
locale
)
    
elif
platform
.
startswith
(
"
macos
"
)
:
        
if
locale
=
=
"
en
-
US
"
:
            
upstream_label
=
"
repackage
-
{
platform
}
/
opt
"
.
format
(
platform
=
platform
)
            
upstream_artifact
=
"
target
.
dmg
"
        
else
:
            
upstream_label
=
"
repackage
-
l10n
-
{
locale
}
-
{
platform
}
/
opt
"
.
format
(
                
locale
=
locale
platform
=
platform
            
)
            
upstream_artifact
=
"
{
locale
}
/
target
.
dmg
"
.
format
(
locale
=
locale
)
    
else
:
        
raise
NotImplementedError
(
            
'
Case
for
platform
"
{
}
"
is
not
implemented
'
.
format
(
platform
)
        
)
    
return
upstream_label
upstream_artifact
def
_build_attribution_config
(
task
task_platforms
attributions
)
:
    
if
any
(
p
.
startswith
(
"
win
"
)
for
p
in
task_platforms
)
:
        
worker
=
task
.
get
(
"
worker
"
{
}
)
        
worker
.
setdefault
(
"
env
"
{
}
)
[
"
ATTRIBUTION_CONFIG
"
]
=
json
.
dumps
(
            
attributions
sort_keys
=
True
        
)
    
elif
any
(
p
.
startswith
(
"
macos
"
)
for
p
in
task_platforms
)
:
        
run
=
task
.
setdefault
(
"
run
"
{
}
)
        
run
[
"
command
"
]
=
build_macos_attribution_dmg_command
(
            
"
/
builds
/
worker
/
fetches
/
dmg
/
dmg
"
attributions
        
)
    
else
:
        
raise
NotImplementedError
(
            
"
Case
for
platforms
{
}
is
not
implemented
"
.
format
(
task_platforms
)
        
)
