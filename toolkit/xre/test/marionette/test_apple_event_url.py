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
Test
that
URLs
delivered
via
macOS
Apple
Events
survive
the
profile
manager
relaunch
.
When
Firefox
is
launched
via
open
https
:
/
/
.
.
.
on
macOS
with
StartWithLastProfile
=
false
the
profile
manager
dialog
appears
and
Firefox
relaunches
after
a
profile
is
selected
.
On
macOS
15
+
URLs
from
Apple
Events
can
be
lost
during
this
relaunch
if
they
arrive
after
InitializeMacApp
(
)
exits
.
See
bug
2036237
.
This
test
automates
the
full
flow
:
sets
StartWithLastProfile
=
false
quits
Firefox
relaunches
via
Apple
Event
with
a
URL
dismisses
the
profile
dialog
with
Enter
and
reconnects
via
Marionette
to
verify
the
URL
was
opened
.
"
"
"
import
os
import
subprocess
import
time
from
marionette_harness
import
MarionetteTestCase
class
TestAppleEventURL
(
MarionetteTestCase
)
:
    
def
setUp
(
self
)
:
        
super
(
)
.
setUp
(
)
        
self
.
original_start_with_last
=
None
        
self
.
original_port
=
self
.
marionette
.
port
    
def
tearDown
(
self
)
:
        
#
Restore
the
original
Marionette
port
in
case
we
changed
it
.
        
self
.
marionette
.
port
=
self
.
original_port
        
#
Restore
startWithLastProfile
if
we
changed
it
.
        
try
:
            
if
(
                
self
.
marionette
.
session
is
not
None
                
and
self
.
original_start_with_last
is
not
None
            
)
:
                
with
self
.
marionette
.
using_context
(
self
.
marionette
.
CONTEXT_CHROME
)
:
                    
self
.
marionette
.
execute_script
(
                        
"
"
"
                        
const
svc
=
Cc
[
"
mozilla
.
org
/
toolkit
/
profile
-
service
;
1
"
]
                            
.
getService
(
Ci
.
nsIToolkitProfileService
)
;
                        
svc
.
startWithLastProfile
=
arguments
[
0
]
;
                        
svc
.
flush
(
)
;
                        
"
"
"
                        
script_args
=
[
self
.
original_start_with_last
]
                        
sandbox
=
"
system
"
                    
)
        
except
Exception
:
            
pass
        
#
Clean
up
extra
tabs
.
        
try
:
            
if
self
.
marionette
.
session
is
not
None
:
                
with
self
.
marionette
.
using_context
(
self
.
marionette
.
CONTEXT_CHROME
)
:
                    
self
.
marionette
.
execute_script
(
                        
"
"
"
                        
for
(
const
win
of
Services
.
wm
.
getEnumerator
(
                            
"
navigator
:
browser
"
                        
)
)
{
                            
while
(
win
.
gBrowser
.
tabs
.
length
>
1
)
{
                                
win
.
gBrowser
.
removeTab
(
win
.
gBrowser
.
tabs
.
at
(
-
1
)
)
;
                            
}
                        
}
                        
"
"
"
                        
sandbox
=
"
system
"
                    
)
        
except
Exception
:
            
pass
        
try
:
            
if
self
.
marionette
.
session
is
not
None
:
                
self
.
marionette
.
quit
(
in_app
=
True
)
        
except
Exception
:
            
pass
        
#
If
we
couldn
'
t
connect
to
the
relaunched
Firefox
it
may
still
be
        
#
running
as
an
orphan
.
Try
to
quit
it
via
osascript
.
        
if
self
.
marionette
.
session
is
None
:
            
process_name
=
self
.
_get_process_name
(
)
            
subprocess
.
run
(
                
[
                    
"
osascript
"
                    
"
-
e
"
                    
f
'
tell
application
"
{
process_name
}
"
to
quit
'
                
]
                
capture_output
=
True
                
timeout
=
10
                
check
=
False
            
)
        
super
(
)
.
tearDown
(
)
    
def
_get_app_bundle_path
(
self
)
:
        
binary
=
self
.
marionette
.
instance
.
binary
        
parts
=
binary
.
split
(
"
/
"
)
        
for
i
part
in
enumerate
(
parts
)
:
            
if
part
.
endswith
(
"
.
app
"
)
:
                
return
"
/
"
.
join
(
parts
[
:
i
+
1
]
)
        
return
None
    
def
_get_process_name
(
self
)
:
        
"
"
"
Derive
the
System
Events
process
name
from
the
app
bundle
.
"
"
"
        
app_bundle
=
self
.
_get_app_bundle_path
(
)
        
if
app_bundle
:
            
#
"
Firefox
Nightly
.
app
"
-
>
"
Firefox
Nightly
"
etc
.
            
return
os
.
path
.
basename
(
app_bundle
)
.
removesuffix
(
"
.
app
"
)
        
return
"
firefox
"
    
def
_wait_for_tab_with_url
(
self
url_substring
timeout
=
10
)
:
        
deadline
=
time
.
monotonic
(
)
+
timeout
        
while
time
.
monotonic
(
)
<
deadline
:
            
with
self
.
marionette
.
using_context
(
self
.
marionette
.
CONTEXT_CHROME
)
:
                
result
=
self
.
marionette
.
execute_script
(
                    
"
"
"
                    
const
substring
=
arguments
[
0
]
;
                    
for
(
const
win
of
Services
.
wm
.
getEnumerator
(
                        
"
navigator
:
browser
"
                    
)
)
{
                        
for
(
const
tab
of
win
.
gBrowser
.
tabs
)
{
                            
const
url
=
tab
.
linkedBrowser
.
currentURI
.
spec
;
                            
if
(
url
.
includes
(
substring
)
)
{
                                
return
url
;
                            
}
                        
}
                    
}
                    
return
null
;
                    
"
"
"
                    
script_args
=
[
url_substring
]
                    
sandbox
=
"
system
"
                
)
                
if
result
:
                    
return
result
            
time
.
sleep
(
0
.
5
)
        
return
None
    
def
test_apple_event_url_survives_profile_manager
(
self
)
:
        
"
"
"
URL
from
Apple
Event
must
survive
the
profile
manager
relaunch
.
"
"
"
        
app_bundle
=
self
.
_get_app_bundle_path
(
)
        
self
.
assertIsNotNone
(
app_bundle
"
Could
not
determine
.
app
bundle
path
"
)
        
test_url
=
"
about
:
license
"
        
#
Save
and
set
startWithLastProfile
=
false
to
trigger
profile
manager
.
        
with
self
.
marionette
.
using_context
(
self
.
marionette
.
CONTEXT_CHROME
)
:
            
self
.
original_start_with_last
=
self
.
marionette
.
execute_script
(
                
"
"
"
                
const
svc
=
Cc
[
"
mozilla
.
org
/
toolkit
/
profile
-
service
;
1
"
]
                    
.
getService
(
Ci
.
nsIToolkitProfileService
)
;
                
const
orig
=
svc
.
startWithLastProfile
;
                
svc
.
startWithLastProfile
=
false
;
                
svc
.
flush
(
)
;
                
return
orig
;
                
"
"
"
                
sandbox
=
"
system
"
            
)
        
#
Quit
Firefox
.
        
self
.
marionette
.
quit
(
)
        
#
Relaunch
via
Apple
Event
.
Use
-
-
env
to
pass
MOZ_MARIONETTE
and
        
#
MOZ_REMOTE_ALLOW_SYSTEM_ACCESS
to
the
launched
app
.
On
macOS
14
+
        
#
open
-
a
does
not
inherit
the
caller
'
s
environment
so
-
-
env
is
        
#
required
.
        
subprocess
.
run
(
            
[
                
"
open
"
                
"
-
a
"
                
app_bundle
                
test_url
                
"
-
-
env
"
                
"
MOZ_MARIONETTE
=
1
"
                
"
-
-
env
"
                
"
MOZ_REMOTE_ALLOW_SYSTEM_ACCESS
=
1
"
            
]
            
check
=
True
            
timeout
=
10
        
)
        
#
Wait
for
the
profile
dialog
to
appear
then
press
Enter
to
accept
        
#
the
default
profile
.
Retry
the
keystroke
in
case
the
dialog
isn
'
t
        
#
ready
yet
.
Note
:
osascript
returning
0
doesn
'
t
guarantee
the
dialog
        
#
was
actually
dismissed
(
the
keystroke
could
go
to
the
wrong
window
)
        
#
but
if
dismissal
fails
the
Marionette
reconnection
and
URL
        
#
verification
below
will
fail
providing
a
clear
error
.
        
process_name
=
self
.
_get_process_name
(
)
        
dialog_dismissed
=
False
        
for
attempt
in
range
(
10
)
:
            
time
.
sleep
(
1
)
            
result
=
subprocess
.
run
(
                
[
                    
"
osascript
"
                    
"
-
e
"
                    
f
'
tell
application
"
System
Events
"
\
n
'
                    
f
'
tell
process
"
{
process_name
}
"
\
n
'
                    
f
"
set
frontmost
to
true
\
n
"
                    
f
"
delay
0
.
5
\
n
"
                    
f
"
keystroke
return
\
n
"
                    
f
"
end
tell
\
n
"
                    
f
"
end
tell
"
                
]
                
capture_output
=
True
                
timeout
=
10
                
check
=
False
            
)
            
if
result
.
returncode
=
=
0
:
                
dialog_dismissed
=
True
                
break
        
self
.
assertTrue
(
            
dialog_dismissed
            
"
Could
not
dismiss
profile
manager
dialog
via
osascript
.
"
            
"
Ensure
System
Events
accessibility
is
enabled
.
"
        
)
        
#
Wait
for
the
relaunched
Firefox
to
start
Marionette
on
the
        
#
default
port
(
2828
)
.
The
relaunched
process
uses
a
different
        
#
profile
and
doesn
'
t
inherit
the
harness
-
assigned
port
.
        
#
NOTE
:
Port
2828
may
conflict
with
parallel
test
jobs
.
See
        
#
bug
2036642
for
proper
Marionette
Apple
Event
launch
support
.
        
from
marionette_driver
import
transport
        
self
.
marionette
.
port
=
2828
        
self
.
marionette
.
raise_for_port
(
timeout
=
30
check_process_status
=
False
)
        
#
Establish
a
new
Marionette
session
on
the
relaunched
instance
.
        
self
.
marionette
.
client
=
transport
.
TcpTransport
(
            
self
.
marionette
.
host
            
2828
            
self
.
marionette
.
socket_timeout
        
)
        
self
.
marionette
.
protocol
_
=
self
.
marionette
.
client
.
connect
(
)
        
resp
=
self
.
marionette
.
_send_message
(
            
"
WebDriver
:
NewSession
"
{
"
strictFileInteractability
"
:
True
}
        
)
        
self
.
marionette
.
session_id
=
resp
[
"
sessionId
"
]
        
self
.
marionette
.
session
=
resp
[
"
capabilities
"
]
        
self
.
marionette
.
cleanup_ran
=
False
        
self
.
marionette
.
process_id
=
self
.
marionette
.
session
.
get
(
"
moz
:
processID
"
)
        
self
.
marionette
.
profile
=
self
.
marionette
.
session
.
get
(
"
moz
:
profile
"
)
        
#
Verify
the
URL
was
opened
.
        
found_url
=
self
.
_wait_for_tab_with_url
(
"
about
:
license
"
)
        
self
.
assertIsNotNone
(
            
found_url
            
"
Expected
about
:
license
to
be
opened
via
Apple
Event
"
            
"
after
profile
manager
relaunch
(
bug
2036237
)
"
        
)
