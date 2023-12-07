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
sys
#
add
this
directory
to
the
path
sys
.
path
.
append
(
os
.
path
.
dirname
(
__file__
)
)
from
session_store_test_case
import
SessionStoreTestCase
def
inline
(
title
)
:
    
return
"
data
:
text
/
html
;
charset
=
utf
-
8
<
html
>
<
head
>
<
title
>
{
}
<
/
title
>
<
/
head
>
<
body
>
<
/
body
>
<
/
html
>
"
.
format
(
        
title
    
)
class
TestSessionRestoreManually
(
SessionStoreTestCase
)
:
    
"
"
"
    
Test
that
window
attributes
for
each
window
are
restored
    
correctly
(
with
manual
session
restore
)
in
a
new
session
.
    
"
"
"
    
def
setUp
(
self
)
:
        
super
(
TestSessionRestoreManually
self
)
.
setUp
(
            
startup_page
=
1
            
include_private
=
False
            
restore_on_demand
=
True
            
test_windows
=
set
(
                
[
                    
#
Window
1
                    
(
                        
inline
(
"
lorem
ipsom
"
)
                        
inline
(
"
dolor
"
)
                    
)
                    
#
Window
2
                    
(
                        
inline
(
"
sit
"
)
                    
)
                
]
            
)
        
)
    
def
test_restore
(
self
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
            
Services
.
prefs
.
setBoolPref
(
"
browser
.
sessionstore
.
persist_closed_tabs_between_sessions
"
true
)
;
            
"
"
"
        
)
        
self
.
wait_for_windows
(
            
self
.
all_windows
"
Not
all
requested
windows
have
been
opened
"
        
)
        
self
.
assertEqual
(
            
len
(
self
.
marionette
.
chrome_window_handles
)
            
2
            
msg
=
"
Should
have
3
windows
open
.
"
        
)
        
self
.
assertEqual
(
            
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
lazy
=
{
}
;
                
ChromeUtils
.
defineESModuleGetters
(
lazy
{
                    
SessionStore
:
"
resource
:
/
/
/
modules
/
sessionstore
/
SessionStore
.
sys
.
mjs
"
                
}
)
;
                
function
getAllBrowserWindows
(
)
{
                    
return
Array
.
from
(
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
;
                
}
                
let
windows
=
getAllBrowserWindows
(
)
;
                
windows
[
1
]
.
resizeTo
(
500
500
)
                
return
windows
[
1
]
.
document
.
documentElement
.
getAttribute
(
"
height
"
)
                
"
"
"
            
)
        
"
500
"
        
"
Window
has
been
set
to
correct
height
"
        
)
        
self
.
marionette
.
quit
(
)
        
self
.
marionette
.
start_session
(
)
        
self
.
marionette
.
set_context
(
"
chrome
"
)
        
#
restore
the
previous
session
        
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
lazy
=
{
}
;
            
ChromeUtils
.
defineESModuleGetters
(
lazy
{
                
SessionStore
:
"
resource
:
/
/
/
modules
/
sessionstore
/
SessionStore
.
sys
.
mjs
"
            
}
)
;
            
function
observeClosedObjectsChange
(
)
{
                
return
new
Promise
(
resolve
=
>
{
                    
function
observe
(
subject
topic
data
)
{
                        
if
(
topic
=
=
"
sessionstore
-
closed
-
objects
-
changed
"
)
{
                            
Services
.
obs
.
removeObserver
(
this
"
sessionstore
-
closed
-
objects
-
changed
"
)
;
                            
resolve
(
'
observed
closed
objects
changed
'
)
;
                        
}
;
                    
}
                    
Services
.
obs
.
addObserver
(
observe
"
sessionstore
-
closed
-
objects
-
changed
"
)
;
                
}
)
;
            
}
;
            
async
function
checkForWindowHeight
(
)
{
                
let
closedWindowsObserver
=
observeClosedObjectsChange
(
)
;
                
lazy
.
SessionStore
.
restoreLastSession
(
)
;
                
await
closedWindowsObserver
;
            
}
            
checkForWindowHeight
(
)
;
            
"
"
"
        
)
        
self
.
assertEqual
(
            
len
(
self
.
marionette
.
chrome_window_handles
)
            
2
            
msg
=
"
Windows
from
last
session
have
been
restored
.
"
        
)
        
self
.
assertEqual
(
            
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
lazy
=
{
}
;
                
ChromeUtils
.
defineESModuleGetters
(
lazy
{
                    
SessionStore
:
"
resource
:
/
/
/
modules
/
sessionstore
/
SessionStore
.
sys
.
mjs
"
                
}
)
;
                
let
state
=
SessionStore
.
getCurrentState
(
)
                
return
state
.
windows
[
1
]
[
"
height
"
]
                
"
"
"
            
)
        
500
        
"
Second
window
has
correct
height
"
        
)
