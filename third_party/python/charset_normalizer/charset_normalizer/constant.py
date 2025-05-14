from
__future__
import
annotations
from
codecs
import
BOM_UTF8
BOM_UTF16_BE
BOM_UTF16_LE
BOM_UTF32_BE
BOM_UTF32_LE
from
encodings
.
aliases
import
aliases
from
re
import
IGNORECASE
from
re
import
compile
as
re_compile
#
Contain
for
each
eligible
encoding
a
list
of
/
item
bytes
SIG
/
BOM
ENCODING_MARKS
:
dict
[
str
bytes
|
list
[
bytes
]
]
=
{
    
"
utf_8
"
:
BOM_UTF8
    
"
utf_7
"
:
[
        
b
"
\
x2b
\
x2f
\
x76
\
x38
"
        
b
"
\
x2b
\
x2f
\
x76
\
x39
"
        
b
"
\
x2b
\
x2f
\
x76
\
x2b
"
        
b
"
\
x2b
\
x2f
\
x76
\
x2f
"
        
b
"
\
x2b
\
x2f
\
x76
\
x38
\
x2d
"
    
]
    
"
gb18030
"
:
b
"
\
x84
\
x31
\
x95
\
x33
"
    
"
utf_32
"
:
[
BOM_UTF32_BE
BOM_UTF32_LE
]
    
"
utf_16
"
:
[
BOM_UTF16_BE
BOM_UTF16_LE
]
}
TOO_SMALL_SEQUENCE
:
int
=
32
TOO_BIG_SEQUENCE
:
int
=
int
(
10e6
)
UTF8_MAXIMAL_ALLOCATION
:
int
=
1_112_064
#
Up
-
to
-
date
Unicode
ucd
/
15
.
0
.
0
UNICODE_RANGES_COMBINED
:
dict
[
str
range
]
=
{
    
"
Control
character
"
:
range
(
32
)
    
"
Basic
Latin
"
:
range
(
32
128
)
    
"
Latin
-
1
Supplement
"
:
range
(
128
256
)
    
"
Latin
Extended
-
A
"
:
range
(
256
384
)
    
"
Latin
Extended
-
B
"
:
range
(
384
592
)
    
"
IPA
Extensions
"
:
range
(
592
688
)
    
"
Spacing
Modifier
Letters
"
:
range
(
688
768
)
    
"
Combining
Diacritical
Marks
"
:
range
(
768
880
)
    
"
Greek
and
Coptic
"
:
range
(
880
1024
)
    
"
Cyrillic
"
:
range
(
1024
1280
)
    
"
Cyrillic
Supplement
"
:
range
(
1280
1328
)
    
"
Armenian
"
:
range
(
1328
1424
)
    
"
Hebrew
"
:
range
(
1424
1536
)
    
"
Arabic
"
:
range
(
1536
1792
)
    
"
Syriac
"
:
range
(
1792
1872
)
    
"
Arabic
Supplement
"
:
range
(
1872
1920
)
    
"
Thaana
"
:
range
(
1920
1984
)
    
"
NKo
"
:
range
(
1984
2048
)
    
"
Samaritan
"
:
range
(
2048
2112
)
    
"
Mandaic
"
:
range
(
2112
2144
)
    
"
Syriac
Supplement
"
:
range
(
2144
2160
)
    
"
Arabic
Extended
-
B
"
:
range
(
2160
2208
)
    
"
Arabic
Extended
-
A
"
:
range
(
2208
2304
)
    
"
Devanagari
"
:
range
(
2304
2432
)
    
"
Bengali
"
:
range
(
2432
2560
)
    
"
Gurmukhi
"
:
range
(
2560
2688
)
    
"
Gujarati
"
:
range
(
2688
2816
)
    
"
Oriya
"
:
range
(
2816
2944
)
    
"
Tamil
"
:
range
(
2944
3072
)
    
"
Telugu
"
:
range
(
3072
3200
)
    
"
Kannada
"
:
range
(
3200
3328
)
    
"
Malayalam
"
:
range
(
3328
3456
)
    
"
Sinhala
"
:
range
(
3456
3584
)
    
"
Thai
"
:
range
(
3584
3712
)
    
"
Lao
"
:
range
(
3712
3840
)
    
"
Tibetan
"
:
range
(
3840
4096
)
    
"
Myanmar
"
:
range
(
4096
4256
)
    
"
Georgian
"
:
range
(
4256
4352
)
    
"
Hangul
Jamo
"
:
range
(
4352
4608
)
    
"
Ethiopic
"
:
range
(
4608
4992
)
    
"
Ethiopic
Supplement
"
:
range
(
4992
5024
)
    
"
Cherokee
"
:
range
(
5024
5120
)
    
"
Unified
Canadian
Aboriginal
Syllabics
"
:
range
(
5120
5760
)
    
"
Ogham
"
:
range
(
5760
5792
)
    
"
Runic
"
:
range
(
5792
5888
)
    
"
Tagalog
"
:
range
(
5888
5920
)
    
"
Hanunoo
"
:
range
(
5920
5952
)
    
"
Buhid
"
:
range
(
5952
5984
)
    
"
Tagbanwa
"
:
range
(
5984
6016
)
    
"
Khmer
"
:
range
(
6016
6144
)
    
"
Mongolian
"
:
range
(
6144
6320
)
    
"
Unified
Canadian
Aboriginal
Syllabics
Extended
"
:
range
(
6320
6400
)
    
"
Limbu
"
:
range
(
6400
6480
)
    
"
Tai
Le
"
:
range
(
6480
6528
)
    
"
New
Tai
Lue
"
:
range
(
6528
6624
)
    
"
Khmer
Symbols
"
:
range
(
6624
6656
)
    
"
Buginese
"
:
range
(
6656
6688
)
    
"
Tai
Tham
"
:
range
(
6688
6832
)
    
"
Combining
Diacritical
Marks
Extended
"
:
range
(
6832
6912
)
    
"
Balinese
"
:
range
(
6912
7040
)
    
"
Sundanese
"
:
range
(
7040
7104
)
    
"
Batak
"
:
range
(
7104
7168
)
    
"
Lepcha
"
:
range
(
7168
7248
)
    
"
Ol
Chiki
"
:
range
(
7248
7296
)
    
"
Cyrillic
Extended
-
C
"
:
range
(
7296
7312
)
    
"
Georgian
Extended
"
:
range
(
7312
7360
)
    
"
Sundanese
Supplement
"
:
range
(
7360
7376
)
    
"
Vedic
Extensions
"
:
range
(
7376
7424
)
    
"
Phonetic
Extensions
"
:
range
(
7424
7552
)
    
"
Phonetic
Extensions
Supplement
"
:
range
(
7552
7616
)
    
"
Combining
Diacritical
Marks
Supplement
"
:
range
(
7616
7680
)
    
"
Latin
Extended
Additional
"
:
range
(
7680
7936
)
    
"
Greek
Extended
"
:
range
(
7936
8192
)
    
"
General
Punctuation
"
:
range
(
8192
8304
)
    
"
Superscripts
and
Subscripts
"
:
range
(
8304
8352
)
    
"
Currency
Symbols
"
:
range
(
8352
8400
)
    
"
Combining
Diacritical
Marks
for
Symbols
"
:
range
(
8400
8448
)
    
"
Letterlike
Symbols
"
:
range
(
8448
8528
)
    
"
Number
Forms
"
:
range
(
8528
8592
)
    
"
Arrows
"
:
range
(
8592
8704
)
    
"
Mathematical
Operators
"
:
range
(
8704
8960
)
    
"
Miscellaneous
Technical
"
:
range
(
8960
9216
)
    
"
Control
Pictures
"
:
range
(
9216
9280
)
    
"
Optical
Character
Recognition
"
:
range
(
9280
9312
)
    
"
Enclosed
Alphanumerics
"
:
range
(
9312
9472
)
    
"
Box
Drawing
"
:
range
(
9472
9600
)
    
"
Block
Elements
"
:
range
(
9600
9632
)
    
"
Geometric
Shapes
"
:
range
(
9632
9728
)
    
"
Miscellaneous
Symbols
"
:
range
(
9728
9984
)
    
"
Dingbats
"
:
range
(
9984
10176
)
    
"
Miscellaneous
Mathematical
Symbols
-
A
"
:
range
(
10176
10224
)
    
"
Supplemental
Arrows
-
A
"
:
range
(
10224
10240
)
    
"
Braille
Patterns
"
:
range
(
10240
10496
)
    
"
Supplemental
Arrows
-
B
"
:
range
(
10496
10624
)
    
"
Miscellaneous
Mathematical
Symbols
-
B
"
:
range
(
10624
10752
)
    
"
Supplemental
Mathematical
Operators
"
:
range
(
10752
11008
)
    
"
Miscellaneous
Symbols
and
Arrows
"
:
range
(
11008
11264
)
    
"
Glagolitic
"
:
range
(
11264
11360
)
    
"
Latin
Extended
-
C
"
:
range
(
11360
11392
)
    
"
Coptic
"
:
range
(
11392
11520
)
    
"
Georgian
Supplement
"
:
range
(
11520
11568
)
    
"
Tifinagh
"
:
range
(
11568
11648
)
    
"
Ethiopic
Extended
"
:
range
(
11648
11744
)
    
"
Cyrillic
Extended
-
A
"
:
range
(
11744
11776
)
    
"
Supplemental
Punctuation
"
:
range
(
11776
11904
)
    
"
CJK
Radicals
Supplement
"
:
range
(
11904
12032
)
    
"
Kangxi
Radicals
"
:
range
(
12032
12256
)
    
"
Ideographic
Description
Characters
"
:
range
(
12272
12288
)
    
"
CJK
Symbols
and
Punctuation
"
:
range
(
12288
12352
)
    
"
Hiragana
"
:
range
(
12352
12448
)
    
"
Katakana
"
:
range
(
12448
12544
)
    
"
Bopomofo
"
:
range
(
12544
12592
)
    
"
Hangul
Compatibility
Jamo
"
:
range
(
12592
12688
)
    
"
Kanbun
"
:
range
(
12688
12704
)
    
"
Bopomofo
Extended
"
:
range
(
12704
12736
)
    
"
CJK
Strokes
"
:
range
(
12736
12784
)
    
"
Katakana
Phonetic
Extensions
"
:
range
(
12784
12800
)
    
"
Enclosed
CJK
Letters
and
Months
"
:
range
(
12800
13056
)
    
"
CJK
Compatibility
"
:
range
(
13056
13312
)
    
"
CJK
Unified
Ideographs
Extension
A
"
:
range
(
13312
19904
)
    
"
Yijing
Hexagram
Symbols
"
:
range
(
19904
19968
)
    
"
CJK
Unified
Ideographs
"
:
range
(
19968
40960
)
    
"
Yi
Syllables
"
:
range
(
40960
42128
)
    
"
Yi
Radicals
"
:
range
(
42128
42192
)
    
"
Lisu
"
:
range
(
42192
42240
)
    
"
Vai
"
:
range
(
42240
42560
)
    
"
Cyrillic
Extended
-
B
"
:
range
(
42560
42656
)
    
"
Bamum
"
:
range
(
42656
42752
)
    
"
Modifier
Tone
Letters
"
:
range
(
42752
42784
)
    
"
Latin
Extended
-
D
"
:
range
(
42784
43008
)
    
"
Syloti
Nagri
"
:
range
(
43008
43056
)
    
"
Common
Indic
Number
Forms
"
:
range
(
43056
43072
)
    
"
Phags
-
pa
"
:
range
(
43072
43136
)
    
"
Saurashtra
"
:
range
(
43136
43232
)
    
"
Devanagari
Extended
"
:
range
(
43232
43264
)
    
"
Kayah
Li
"
:
range
(
43264
43312
)
    
"
Rejang
"
:
range
(
43312
43360
)
    
"
Hangul
Jamo
Extended
-
A
"
:
range
(
43360
43392
)
    
"
Javanese
"
:
range
(
43392
43488
)
    
"
Myanmar
Extended
-
B
"
:
range
(
43488
43520
)
    
"
Cham
"
:
range
(
43520
43616
)
    
"
Myanmar
Extended
-
A
"
:
range
(
43616
43648
)
    
"
Tai
Viet
"
:
range
(
43648
43744
)
    
"
Meetei
Mayek
Extensions
"
:
range
(
43744
43776
)
    
"
Ethiopic
Extended
-
A
"
:
range
(
43776
43824
)
    
"
Latin
Extended
-
E
"
:
range
(
43824
43888
)
    
"
Cherokee
Supplement
"
:
range
(
43888
43968
)
    
"
Meetei
Mayek
"
:
range
(
43968
44032
)
    
"
Hangul
Syllables
"
:
range
(
44032
55216
)
    
"
Hangul
Jamo
Extended
-
B
"
:
range
(
55216
55296
)
    
"
High
Surrogates
"
:
range
(
55296
56192
)
    
"
High
Private
Use
Surrogates
"
:
range
(
56192
56320
)
    
"
Low
Surrogates
"
:
range
(
56320
57344
)
    
"
Private
Use
Area
"
:
range
(
57344
63744
)
    
"
CJK
Compatibility
Ideographs
"
:
range
(
63744
64256
)
    
"
Alphabetic
Presentation
Forms
"
:
range
(
64256
64336
)
    
"
Arabic
Presentation
Forms
-
A
"
:
range
(
64336
65024
)
    
"
Variation
Selectors
"
:
range
(
65024
65040
)
    
"
Vertical
Forms
"
:
range
(
65040
65056
)
    
"
Combining
Half
Marks
"
:
range
(
65056
65072
)
    
"
CJK
Compatibility
Forms
"
:
range
(
65072
65104
)
    
"
Small
Form
Variants
"
:
range
(
65104
65136
)
    
"
Arabic
Presentation
Forms
-
B
"
:
range
(
65136
65280
)
    
"
Halfwidth
and
Fullwidth
Forms
"
:
range
(
65280
65520
)
    
"
Specials
"
:
range
(
65520
65536
)
    
"
Linear
B
Syllabary
"
:
range
(
65536
65664
)
    
"
Linear
B
Ideograms
"
:
range
(
65664
65792
)
    
"
Aegean
Numbers
"
:
range
(
65792
65856
)
    
"
Ancient
Greek
Numbers
"
:
range
(
65856
65936
)
    
"
Ancient
Symbols
"
:
range
(
65936
66000
)
    
"
Phaistos
Disc
"
:
range
(
66000
66048
)
    
"
Lycian
"
:
range
(
66176
66208
)
    
"
Carian
"
:
range
(
66208
66272
)
    
"
Coptic
Epact
Numbers
"
:
range
(
66272
66304
)
    
"
Old
Italic
"
:
range
(
66304
66352
)
    
"
Gothic
"
:
range
(
66352
66384
)
    
"
Old
Permic
"
:
range
(
66384
66432
)
    
"
Ugaritic
"
:
range
(
66432
66464
)
    
"
Old
Persian
"
:
range
(
66464
66528
)
    
"
Deseret
"
:
range
(
66560
66640
)
    
"
Shavian
"
:
range
(
66640
66688
)
    
"
Osmanya
"
:
range
(
66688
66736
)
    
"
Osage
"
:
range
(
66736
66816
)
    
"
Elbasan
"
:
range
(
66816
66864
)
    
"
Caucasian
Albanian
"
:
range
(
66864
66928
)
    
"
Vithkuqi
"
:
range
(
66928
67008
)
    
"
Linear
A
"
:
range
(
67072
67456
)
    
"
Latin
Extended
-
F
"
:
range
(
67456
67520
)
    
"
Cypriot
Syllabary
"
:
range
(
67584
67648
)
    
"
Imperial
Aramaic
"
:
range
(
67648
67680
)
    
"
Palmyrene
"
:
range
(
67680
67712
)
    
"
Nabataean
"
:
range
(
67712
67760
)
    
"
Hatran
"
:
range
(
67808
67840
)
    
"
Phoenician
"
:
range
(
67840
67872
)
    
"
Lydian
"
:
range
(
67872
67904
)
    
"
Meroitic
Hieroglyphs
"
:
range
(
67968
68000
)
    
"
Meroitic
Cursive
"
:
range
(
68000
68096
)
    
"
Kharoshthi
"
:
range
(
68096
68192
)
    
"
Old
South
Arabian
"
:
range
(
68192
68224
)
    
"
Old
North
Arabian
"
:
range
(
68224
68256
)
    
"
Manichaean
"
:
range
(
68288
68352
)
    
"
Avestan
"
:
range
(
68352
68416
)
    
"
Inscriptional
Parthian
"
:
range
(
68416
68448
)
    
"
Inscriptional
Pahlavi
"
:
range
(
68448
68480
)
    
"
Psalter
Pahlavi
"
:
range
(
68480
68528
)
    
"
Old
Turkic
"
:
range
(
68608
68688
)
    
"
Old
Hungarian
"
:
range
(
68736
68864
)
    
"
Hanifi
Rohingya
"
:
range
(
68864
68928
)
    
"
Rumi
Numeral
Symbols
"
:
range
(
69216
69248
)
    
"
Yezidi
"
:
range
(
69248
69312
)
    
"
Arabic
Extended
-
C
"
:
range
(
69312
69376
)
    
"
Old
Sogdian
"
:
range
(
69376
69424
)
    
"
Sogdian
"
:
range
(
69424
69488
)
    
"
Old
Uyghur
"
:
range
(
69488
69552
)
    
"
Chorasmian
"
:
range
(
69552
69600
)
    
"
Elymaic
"
:
range
(
69600
69632
)
    
"
Brahmi
"
:
range
(
69632
69760
)
    
"
Kaithi
"
:
range
(
69760
69840
)
    
"
Sora
Sompeng
"
:
range
(
69840
69888
)
    
"
Chakma
"
:
range
(
69888
69968
)
    
"
Mahajani
"
:
range
(
69968
70016
)
    
"
Sharada
"
:
range
(
70016
70112
)
    
"
Sinhala
Archaic
Numbers
"
:
range
(
70112
70144
)
    
"
Khojki
"
:
range
(
70144
70224
)
    
"
Multani
"
:
range
(
70272
70320
)
    
"
Khudawadi
"
:
range
(
70320
70400
)
    
"
Grantha
"
:
range
(
70400
70528
)
    
"
Newa
"
:
range
(
70656
70784
)
    
"
Tirhuta
"
:
range
(
70784
70880
)
    
"
Siddham
"
:
range
(
71040
71168
)
    
"
Modi
"
:
range
(
71168
71264
)
    
"
Mongolian
Supplement
"
:
range
(
71264
71296
)
    
"
Takri
"
:
range
(
71296
71376
)
    
"
Ahom
"
:
range
(
71424
71504
)
    
"
Dogra
"
:
range
(
71680
71760
)
    
"
Warang
Citi
"
:
range
(
71840
71936
)
    
"
Dives
Akuru
"
:
range
(
71936
72032
)
    
"
Nandinagari
"
:
range
(
72096
72192
)
    
"
Zanabazar
Square
"
:
range
(
72192
72272
)
    
"
Soyombo
"
:
range
(
72272
72368
)
    
"
Unified
Canadian
Aboriginal
Syllabics
Extended
-
A
"
:
range
(
72368
72384
)
    
"
Pau
Cin
Hau
"
:
range
(
72384
72448
)
    
"
Devanagari
Extended
-
A
"
:
range
(
72448
72544
)
    
"
Bhaiksuki
"
:
range
(
72704
72816
)
    
"
Marchen
"
:
range
(
72816
72896
)
    
"
Masaram
Gondi
"
:
range
(
72960
73056
)
    
"
Gunjala
Gondi
"
:
range
(
73056
73136
)
    
"
Makasar
"
:
range
(
73440
73472
)
    
"
Kawi
"
:
range
(
73472
73568
)
    
"
Lisu
Supplement
"
:
range
(
73648
73664
)
    
"
Tamil
Supplement
"
:
range
(
73664
73728
)
    
"
Cuneiform
"
:
range
(
73728
74752
)
    
"
Cuneiform
Numbers
and
Punctuation
"
:
range
(
74752
74880
)
    
"
Early
Dynastic
Cuneiform
"
:
range
(
74880
75088
)
    
"
Cypro
-
Minoan
"
:
range
(
77712
77824
)
    
"
Egyptian
Hieroglyphs
"
:
range
(
77824
78896
)
    
"
Egyptian
Hieroglyph
Format
Controls
"
:
range
(
78896
78944
)
    
"
Anatolian
Hieroglyphs
"
:
range
(
82944
83584
)
    
"
Bamum
Supplement
"
:
range
(
92160
92736
)
    
"
Mro
"
:
range
(
92736
92784
)
    
"
Tangsa
"
:
range
(
92784
92880
)
    
"
Bassa
Vah
"
:
range
(
92880
92928
)
    
"
Pahawh
Hmong
"
:
range
(
92928
93072
)
    
"
Medefaidrin
"
:
range
(
93760
93856
)
    
"
Miao
"
:
range
(
93952
94112
)
    
"
Ideographic
Symbols
and
Punctuation
"
:
range
(
94176
94208
)
    
"
Tangut
"
:
range
(
94208
100352
)
    
"
Tangut
Components
"
:
range
(
100352
101120
)
    
"
Khitan
Small
Script
"
:
range
(
101120
101632
)
    
"
Tangut
Supplement
"
:
range
(
101632
101760
)
    
"
Kana
Extended
-
B
"
:
range
(
110576
110592
)
    
"
Kana
Supplement
"
:
range
(
110592
110848
)
    
"
Kana
Extended
-
A
"
:
range
(
110848
110896
)
    
"
Small
Kana
Extension
"
:
range
(
110896
110960
)
    
"
Nushu
"
:
range
(
110960
111360
)
    
"
Duployan
"
:
range
(
113664
113824
)
    
"
Shorthand
Format
Controls
"
:
range
(
113824
113840
)
    
"
Znamenny
Musical
Notation
"
:
range
(
118528
118736
)
    
"
Byzantine
Musical
Symbols
"
:
range
(
118784
119040
)
    
"
Musical
Symbols
"
:
range
(
119040
119296
)
    
"
Ancient
Greek
Musical
Notation
"
:
range
(
119296
119376
)
    
"
Kaktovik
Numerals
"
:
range
(
119488
119520
)
    
"
Mayan
Numerals
"
:
range
(
119520
119552
)
    
"
Tai
Xuan
Jing
Symbols
"
:
range
(
119552
119648
)
    
"
Counting
Rod
Numerals
"
:
range
(
119648
119680
)
    
"
Mathematical
Alphanumeric
Symbols
"
:
range
(
119808
120832
)
    
"
Sutton
SignWriting
"
:
range
(
120832
121520
)
    
"
Latin
Extended
-
G
"
:
range
(
122624
122880
)
    
"
Glagolitic
Supplement
"
:
range
(
122880
122928
)
    
"
Cyrillic
Extended
-
D
"
:
range
(
122928
123024
)
    
"
Nyiakeng
Puachue
Hmong
"
:
range
(
123136
123216
)
    
"
Toto
"
:
range
(
123536
123584
)
    
"
Wancho
"
:
range
(
123584
123648
)
    
"
Nag
Mundari
"
:
range
(
124112
124160
)
    
"
Ethiopic
Extended
-
B
"
:
range
(
124896
124928
)
    
"
Mende
Kikakui
"
:
range
(
124928
125152
)
    
"
Adlam
"
:
range
(
125184
125280
)
    
"
Indic
Siyaq
Numbers
"
:
range
(
126064
126144
)
    
"
Ottoman
Siyaq
Numbers
"
:
range
(
126208
126288
)
    
"
Arabic
Mathematical
Alphabetic
Symbols
"
:
range
(
126464
126720
)
    
"
Mahjong
Tiles
"
:
range
(
126976
127024
)
    
"
Domino
Tiles
"
:
range
(
127024
127136
)
    
"
Playing
Cards
"
:
range
(
127136
127232
)
    
"
Enclosed
Alphanumeric
Supplement
"
:
range
(
127232
127488
)
    
"
Enclosed
Ideographic
Supplement
"
:
range
(
127488
127744
)
    
"
Miscellaneous
Symbols
and
Pictographs
"
:
range
(
127744
128512
)
    
"
Emoticons
range
(
Emoji
)
"
:
range
(
128512
128592
)
    
"
Ornamental
Dingbats
"
:
range
(
128592
128640
)
    
"
Transport
and
Map
Symbols
"
:
range
(
128640
128768
)
    
"
Alchemical
Symbols
"
:
range
(
128768
128896
)
    
"
Geometric
Shapes
Extended
"
:
range
(
128896
129024
)
    
"
Supplemental
Arrows
-
C
"
:
range
(
129024
129280
)
    
"
Supplemental
Symbols
and
Pictographs
"
:
range
(
129280
129536
)
    
"
Chess
Symbols
"
:
range
(
129536
129648
)
    
"
Symbols
and
Pictographs
Extended
-
A
"
:
range
(
129648
129792
)
    
"
Symbols
for
Legacy
Computing
"
:
range
(
129792
130048
)
    
"
CJK
Unified
Ideographs
Extension
B
"
:
range
(
131072
173792
)
    
"
CJK
Unified
Ideographs
Extension
C
"
:
range
(
173824
177984
)
    
"
CJK
Unified
Ideographs
Extension
D
"
:
range
(
177984
178208
)
    
"
CJK
Unified
Ideographs
Extension
E
"
:
range
(
178208
183984
)
    
"
CJK
Unified
Ideographs
Extension
F
"
:
range
(
183984
191472
)
    
"
CJK
Compatibility
Ideographs
Supplement
"
:
range
(
194560
195104
)
    
"
CJK
Unified
Ideographs
Extension
G
"
:
range
(
196608
201552
)
    
"
CJK
Unified
Ideographs
Extension
H
"
:
range
(
201552
205744
)
    
"
Tags
"
:
range
(
917504
917632
)
    
"
Variation
Selectors
Supplement
"
:
range
(
917760
918000
)
    
"
Supplementary
Private
Use
Area
-
A
"
:
range
(
983040
1048576
)
    
"
Supplementary
Private
Use
Area
-
B
"
:
range
(
1048576
1114112
)
}
UNICODE_SECONDARY_RANGE_KEYWORD
:
list
[
str
]
=
[
    
"
Supplement
"
    
"
Extended
"
    
"
Extensions
"
    
"
Modifier
"
    
"
Marks
"
    
"
Punctuation
"
    
"
Symbols
"
    
"
Forms
"
    
"
Operators
"
    
"
Miscellaneous
"
    
"
Drawing
"
    
"
Block
"
    
"
Shapes
"
    
"
Supplemental
"
    
"
Tags
"
]
RE_POSSIBLE_ENCODING_INDICATION
=
re_compile
(
    
r
"
(
?
:
(
?
:
encoding
)
|
(
?
:
charset
)
|
(
?
:
coding
)
)
(
?
:
[
\
:
=
]
{
1
10
}
)
(
?
:
[
\
"
\
'
]
?
)
(
[
a
-
zA
-
Z0
-
9
\
-
_
]
+
)
(
?
:
[
\
"
\
'
]
?
)
"
    
IGNORECASE
)
IANA_NO_ALIASES
=
[
    
"
cp720
"
    
"
cp737
"
    
"
cp856
"
    
"
cp874
"
    
"
cp875
"
    
"
cp1006
"
    
"
koi8_r
"
    
"
koi8_t
"
    
"
koi8_u
"
]
IANA_SUPPORTED
:
list
[
str
]
=
sorted
(
    
filter
(
        
lambda
x
:
x
.
endswith
(
"
_codec
"
)
is
False
        
and
x
not
in
{
"
rot_13
"
"
tactis
"
"
mbcs
"
}
        
list
(
set
(
aliases
.
values
(
)
)
)
+
IANA_NO_ALIASES
    
)
)
IANA_SUPPORTED_COUNT
:
int
=
len
(
IANA_SUPPORTED
)
#
pre
-
computed
code
page
that
are
similar
using
the
function
cp_similarity
.
IANA_SUPPORTED_SIMILAR
:
dict
[
str
list
[
str
]
]
=
{
    
"
cp037
"
:
[
"
cp1026
"
"
cp1140
"
"
cp273
"
"
cp500
"
]
    
"
cp1026
"
:
[
"
cp037
"
"
cp1140
"
"
cp273
"
"
cp500
"
]
    
"
cp1125
"
:
[
"
cp866
"
]
    
"
cp1140
"
:
[
"
cp037
"
"
cp1026
"
"
cp273
"
"
cp500
"
]
    
"
cp1250
"
:
[
"
iso8859_2
"
]
    
"
cp1251
"
:
[
"
kz1048
"
"
ptcp154
"
]
    
"
cp1252
"
:
[
"
iso8859_15
"
"
iso8859_9
"
"
latin_1
"
]
    
"
cp1253
"
:
[
"
iso8859_7
"
]
    
"
cp1254
"
:
[
"
iso8859_15
"
"
iso8859_9
"
"
latin_1
"
]
    
"
cp1257
"
:
[
"
iso8859_13
"
]
    
"
cp273
"
:
[
"
cp037
"
"
cp1026
"
"
cp1140
"
"
cp500
"
]
    
"
cp437
"
:
[
"
cp850
"
"
cp858
"
"
cp860
"
"
cp861
"
"
cp862
"
"
cp863
"
"
cp865
"
]
    
"
cp500
"
:
[
"
cp037
"
"
cp1026
"
"
cp1140
"
"
cp273
"
]
    
"
cp850
"
:
[
"
cp437
"
"
cp857
"
"
cp858
"
"
cp865
"
]
    
"
cp857
"
:
[
"
cp850
"
"
cp858
"
"
cp865
"
]
    
"
cp858
"
:
[
"
cp437
"
"
cp850
"
"
cp857
"
"
cp865
"
]
    
"
cp860
"
:
[
"
cp437
"
"
cp861
"
"
cp862
"
"
cp863
"
"
cp865
"
]
    
"
cp861
"
:
[
"
cp437
"
"
cp860
"
"
cp862
"
"
cp863
"
"
cp865
"
]
    
"
cp862
"
:
[
"
cp437
"
"
cp860
"
"
cp861
"
"
cp863
"
"
cp865
"
]
    
"
cp863
"
:
[
"
cp437
"
"
cp860
"
"
cp861
"
"
cp862
"
"
cp865
"
]
    
"
cp865
"
:
[
"
cp437
"
"
cp850
"
"
cp857
"
"
cp858
"
"
cp860
"
"
cp861
"
"
cp862
"
"
cp863
"
]
    
"
cp866
"
:
[
"
cp1125
"
]
    
"
iso8859_10
"
:
[
"
iso8859_14
"
"
iso8859_15
"
"
iso8859_4
"
"
iso8859_9
"
"
latin_1
"
]
    
"
iso8859_11
"
:
[
"
tis_620
"
]
    
"
iso8859_13
"
:
[
"
cp1257
"
]
    
"
iso8859_14
"
:
[
        
"
iso8859_10
"
        
"
iso8859_15
"
        
"
iso8859_16
"
        
"
iso8859_3
"
        
"
iso8859_9
"
        
"
latin_1
"
    
]
    
"
iso8859_15
"
:
[
        
"
cp1252
"
        
"
cp1254
"
        
"
iso8859_10
"
        
"
iso8859_14
"
        
"
iso8859_16
"
        
"
iso8859_3
"
        
"
iso8859_9
"
        
"
latin_1
"
    
]
    
"
iso8859_16
"
:
[
        
"
iso8859_14
"
        
"
iso8859_15
"
        
"
iso8859_2
"
        
"
iso8859_3
"
        
"
iso8859_9
"
        
"
latin_1
"
    
]
    
"
iso8859_2
"
:
[
"
cp1250
"
"
iso8859_16
"
"
iso8859_4
"
]
    
"
iso8859_3
"
:
[
"
iso8859_14
"
"
iso8859_15
"
"
iso8859_16
"
"
iso8859_9
"
"
latin_1
"
]
    
"
iso8859_4
"
:
[
"
iso8859_10
"
"
iso8859_2
"
"
iso8859_9
"
"
latin_1
"
]
    
"
iso8859_7
"
:
[
"
cp1253
"
]
    
"
iso8859_9
"
:
[
        
"
cp1252
"
        
"
cp1254
"
        
"
cp1258
"
        
"
iso8859_10
"
        
"
iso8859_14
"
        
"
iso8859_15
"
        
"
iso8859_16
"
        
"
iso8859_3
"
        
"
iso8859_4
"
        
"
latin_1
"
    
]
    
"
kz1048
"
:
[
"
cp1251
"
"
ptcp154
"
]
    
"
latin_1
"
:
[
        
"
cp1252
"
        
"
cp1254
"
        
"
cp1258
"
        
"
iso8859_10
"
        
"
iso8859_14
"
        
"
iso8859_15
"
        
"
iso8859_16
"
        
"
iso8859_3
"
        
"
iso8859_4
"
        
"
iso8859_9
"
    
]
    
"
mac_iceland
"
:
[
"
mac_roman
"
"
mac_turkish
"
]
    
"
mac_roman
"
:
[
"
mac_iceland
"
"
mac_turkish
"
]
    
"
mac_turkish
"
:
[
"
mac_iceland
"
"
mac_roman
"
]
    
"
ptcp154
"
:
[
"
cp1251
"
"
kz1048
"
]
    
"
tis_620
"
:
[
"
iso8859_11
"
]
}
CHARDET_CORRESPONDENCE
:
dict
[
str
str
]
=
{
    
"
iso2022_kr
"
:
"
ISO
-
2022
-
KR
"
    
"
iso2022_jp
"
:
"
ISO
-
2022
-
JP
"
    
"
euc_kr
"
:
"
EUC
-
KR
"
    
"
tis_620
"
:
"
TIS
-
620
"
    
"
utf_32
"
:
"
UTF
-
32
"
    
"
euc_jp
"
:
"
EUC
-
JP
"
    
"
koi8_r
"
:
"
KOI8
-
R
"
    
"
iso8859_1
"
:
"
ISO
-
8859
-
1
"
    
"
iso8859_2
"
:
"
ISO
-
8859
-
2
"
    
"
iso8859_5
"
:
"
ISO
-
8859
-
5
"
    
"
iso8859_6
"
:
"
ISO
-
8859
-
6
"
    
"
iso8859_7
"
:
"
ISO
-
8859
-
7
"
    
"
iso8859_8
"
:
"
ISO
-
8859
-
8
"
    
"
utf_16
"
:
"
UTF
-
16
"
    
"
cp855
"
:
"
IBM855
"
    
"
mac_cyrillic
"
:
"
MacCyrillic
"
    
"
gb2312
"
:
"
GB2312
"
    
"
gb18030
"
:
"
GB18030
"
    
"
cp932
"
:
"
CP932
"
    
"
cp866
"
:
"
IBM866
"
    
"
utf_8
"
:
"
utf
-
8
"
    
"
utf_8_sig
"
:
"
UTF
-
8
-
SIG
"
    
"
shift_jis
"
:
"
SHIFT_JIS
"
    
"
big5
"
:
"
Big5
"
    
"
cp1250
"
:
"
windows
-
1250
"
    
"
cp1251
"
:
"
windows
-
1251
"
    
"
cp1252
"
:
"
Windows
-
1252
"
    
"
cp1253
"
:
"
windows
-
1253
"
    
"
cp1255
"
:
"
windows
-
1255
"
    
"
cp1256
"
:
"
windows
-
1256
"
    
"
cp1254
"
:
"
Windows
-
1254
"
    
"
cp949
"
:
"
CP949
"
}
COMMON_SAFE_ASCII_CHARACTERS
:
set
[
str
]
=
{
    
"
<
"
    
"
>
"
    
"
=
"
    
"
:
"
    
"
/
"
    
"
&
"
    
"
;
"
    
"
{
"
    
"
}
"
    
"
[
"
    
"
]
"
    
"
"
    
"
|
"
    
'
"
'
    
"
-
"
    
"
(
"
    
"
)
"
}
#
Sample
character
sets
replace
with
full
lists
if
needed
COMMON_CHINESE_CHARACTERS
=
"
"
COMMON_JAPANESE_CHARACTERS
=
"
"
COMMON_KOREAN_CHARACTERS
=
"
"
#
Combine
all
into
a
set
COMMON_CJK_CHARACTERS
=
set
(
    
"
"
.
join
(
        
[
            
COMMON_CHINESE_CHARACTERS
            
COMMON_JAPANESE_CHARACTERS
            
COMMON_KOREAN_CHARACTERS
        
]
    
)
)
KO_NAMES
:
set
[
str
]
=
{
"
johab
"
"
cp949
"
"
euc_kr
"
}
ZH_NAMES
:
set
[
str
]
=
{
"
big5
"
"
cp950
"
"
big5hkscs
"
"
hz
"
}
#
Logging
LEVEL
below
DEBUG
TRACE
:
int
=
5
#
Language
label
that
contain
the
em
dash
"
"
#
character
are
to
be
considered
alternative
seq
to
origin
FREQUENCIES
:
dict
[
str
list
[
str
]
]
=
{
    
"
English
"
:
[
        
"
e
"
        
"
a
"
        
"
t
"
        
"
i
"
        
"
o
"
        
"
n
"
        
"
s
"
        
"
r
"
        
"
h
"
        
"
l
"
        
"
d
"
        
"
c
"
        
"
u
"
        
"
m
"
        
"
f
"
        
"
p
"
        
"
g
"
        
"
w
"
        
"
y
"
        
"
b
"
        
"
v
"
        
"
k
"
        
"
x
"
        
"
j
"
        
"
z
"
        
"
q
"
    
]
    
"
English
"
:
[
        
"
e
"
        
"
a
"
        
"
t
"
        
"
i
"
        
"
o
"
        
"
n
"
        
"
s
"
        
"
r
"
        
"
h
"
        
"
l
"
        
"
d
"
        
"
c
"
        
"
m
"
        
"
u
"
        
"
f
"
        
"
p
"
        
"
g
"
        
"
w
"
        
"
b
"
        
"
y
"
        
"
v
"
        
"
k
"
        
"
j
"
        
"
x
"
        
"
z
"
        
"
q
"
    
]
    
"
German
"
:
[
        
"
e
"
        
"
n
"
        
"
i
"
        
"
r
"
        
"
s
"
        
"
t
"
        
"
a
"
        
"
d
"
        
"
h
"
        
"
u
"
        
"
l
"
        
"
g
"
        
"
o
"
        
"
c
"
        
"
m
"
        
"
b
"
        
"
f
"
        
"
k
"
        
"
w
"
        
"
z
"
        
"
p
"
        
"
v
"
        
"
"
        
"
"
        
"
"
        
"
j
"
    
]
    
"
French
"
:
[
        
"
e
"
        
"
a
"
        
"
s
"
        
"
n
"
        
"
i
"
        
"
t
"
        
"
r
"
        
"
l
"
        
"
u
"
        
"
o
"
        
"
d
"
        
"
c
"
        
"
p
"
        
"
m
"
        
"
"
        
"
v
"
        
"
g
"
        
"
f
"
        
"
b
"
        
"
h
"
        
"
q
"
        
"
"
        
"
x
"
        
"
"
        
"
y
"
        
"
j
"
    
]
    
"
Dutch
"
:
[
        
"
e
"
        
"
n
"
        
"
a
"
        
"
i
"
        
"
r
"
        
"
t
"
        
"
o
"
        
"
d
"
        
"
s
"
        
"
l
"
        
"
g
"
        
"
h
"
        
"
v
"
        
"
m
"
        
"
u
"
        
"
k
"
        
"
c
"
        
"
p
"
        
"
b
"
        
"
w
"
        
"
j
"
        
"
z
"
        
"
f
"
        
"
y
"
        
"
x
"
        
"
"
    
]
    
"
Italian
"
:
[
        
"
e
"
        
"
i
"
        
"
a
"
        
"
o
"
        
"
n
"
        
"
l
"
        
"
t
"
        
"
r
"
        
"
s
"
        
"
c
"
        
"
d
"
        
"
u
"
        
"
p
"
        
"
m
"
        
"
g
"
        
"
v
"
        
"
f
"
        
"
b
"
        
"
z
"
        
"
h
"
        
"
q
"
        
"
"
        
"
"
        
"
k
"
        
"
y
"
        
"
"
    
]
    
"
Polish
"
:
[
        
"
a
"
        
"
i
"
        
"
o
"
        
"
e
"
        
"
n
"
        
"
r
"
        
"
z
"
        
"
w
"
        
"
s
"
        
"
c
"
        
"
t
"
        
"
k
"
        
"
y
"
        
"
d
"
        
"
p
"
        
"
m
"
        
"
u
"
        
"
l
"
        
"
j
"
        
"
"
        
"
g
"
        
"
b
"
        
"
h
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Spanish
"
:
[
        
"
e
"
        
"
a
"
        
"
o
"
        
"
n
"
        
"
s
"
        
"
r
"
        
"
i
"
        
"
l
"
        
"
d
"
        
"
t
"
        
"
c
"
        
"
u
"
        
"
m
"
        
"
p
"
        
"
b
"
        
"
g
"
        
"
v
"
        
"
f
"
        
"
y
"
        
"
"
        
"
h
"
        
"
q
"
        
"
"
        
"
j
"
        
"
z
"
        
"
"
    
]
    
"
Russian
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
#
Jap
-
Kanji
    
"
Japanese
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
#
Jap
-
Katakana
    
"
Japanese
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
#
Jap
-
Hiragana
    
"
Japanese
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Portuguese
"
:
[
        
"
a
"
        
"
e
"
        
"
o
"
        
"
s
"
        
"
i
"
        
"
r
"
        
"
d
"
        
"
n
"
        
"
t
"
        
"
m
"
        
"
u
"
        
"
c
"
        
"
l
"
        
"
p
"
        
"
g
"
        
"
v
"
        
"
b
"
        
"
f
"
        
"
h
"
        
"
"
        
"
q
"
        
"
"
        
"
"
        
"
"
        
"
z
"
        
"
"
    
]
    
"
Swedish
"
:
[
        
"
e
"
        
"
a
"
        
"
n
"
        
"
r
"
        
"
t
"
        
"
s
"
        
"
i
"
        
"
l
"
        
"
d
"
        
"
o
"
        
"
m
"
        
"
k
"
        
"
g
"
        
"
v
"
        
"
h
"
        
"
f
"
        
"
u
"
        
"
p
"
        
"
"
        
"
c
"
        
"
b
"
        
"
"
        
"
"
        
"
y
"
        
"
j
"
        
"
x
"
    
]
    
"
Chinese
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Ukrainian
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Norwegian
"
:
[
        
"
e
"
        
"
r
"
        
"
n
"
        
"
t
"
        
"
a
"
        
"
s
"
        
"
i
"
        
"
o
"
        
"
l
"
        
"
d
"
        
"
g
"
        
"
k
"
        
"
m
"
        
"
v
"
        
"
f
"
        
"
p
"
        
"
u
"
        
"
b
"
        
"
h
"
        
"
"
        
"
y
"
        
"
j
"
        
"
"
        
"
c
"
        
"
"
        
"
w
"
    
]
    
"
Finnish
"
:
[
        
"
a
"
        
"
i
"
        
"
n
"
        
"
t
"
        
"
e
"
        
"
s
"
        
"
l
"
        
"
o
"
        
"
u
"
        
"
k
"
        
"
"
        
"
m
"
        
"
r
"
        
"
v
"
        
"
j
"
        
"
h
"
        
"
p
"
        
"
y
"
        
"
d
"
        
"
"
        
"
g
"
        
"
c
"
        
"
b
"
        
"
f
"
        
"
w
"
        
"
z
"
    
]
    
"
Vietnamese
"
:
[
        
"
n
"
        
"
h
"
        
"
t
"
        
"
i
"
        
"
c
"
        
"
g
"
        
"
a
"
        
"
o
"
        
"
u
"
        
"
m
"
        
"
l
"
        
"
r
"
        
"
"
        
"
"
        
"
s
"
        
"
e
"
        
"
v
"
        
"
p
"
        
"
b
"
        
"
y
"
        
"
"
        
"
d
"
        
"
"
        
"
k
"
        
"
"
        
"
"
    
]
    
"
Czech
"
:
[
        
"
o
"
        
"
e
"
        
"
a
"
        
"
n
"
        
"
t
"
        
"
s
"
        
"
i
"
        
"
l
"
        
"
v
"
        
"
r
"
        
"
k
"
        
"
d
"
        
"
u
"
        
"
m
"
        
"
p
"
        
"
"
        
"
c
"
        
"
h
"
        
"
z
"
        
"
"
        
"
y
"
        
"
j
"
        
"
b
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Hungarian
"
:
[
        
"
e
"
        
"
a
"
        
"
t
"
        
"
l
"
        
"
s
"
        
"
n
"
        
"
k
"
        
"
r
"
        
"
i
"
        
"
o
"
        
"
z
"
        
"
"
        
"
"
        
"
g
"
        
"
m
"
        
"
b
"
        
"
y
"
        
"
v
"
        
"
d
"
        
"
h
"
        
"
u
"
        
"
p
"
        
"
j
"
        
"
"
        
"
f
"
        
"
c
"
    
]
    
"
Korean
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Indonesian
"
:
[
        
"
a
"
        
"
n
"
        
"
e
"
        
"
i
"
        
"
r
"
        
"
t
"
        
"
u
"
        
"
s
"
        
"
d
"
        
"
k
"
        
"
m
"
        
"
l
"
        
"
g
"
        
"
p
"
        
"
b
"
        
"
o
"
        
"
h
"
        
"
y
"
        
"
j
"
        
"
c
"
        
"
w
"
        
"
f
"
        
"
v
"
        
"
z
"
        
"
x
"
        
"
q
"
    
]
    
"
Turkish
"
:
[
        
"
a
"
        
"
e
"
        
"
i
"
        
"
n
"
        
"
r
"
        
"
l
"
        
"
"
        
"
k
"
        
"
d
"
        
"
t
"
        
"
s
"
        
"
m
"
        
"
y
"
        
"
u
"
        
"
o
"
        
"
b
"
        
"
"
        
"
"
        
"
v
"
        
"
g
"
        
"
z
"
        
"
h
"
        
"
c
"
        
"
p
"
        
"
"
        
"
"
    
]
    
"
Romanian
"
:
[
        
"
e
"
        
"
i
"
        
"
a
"
        
"
r
"
        
"
n
"
        
"
t
"
        
"
u
"
        
"
l
"
        
"
o
"
        
"
c
"
        
"
s
"
        
"
d
"
        
"
p
"
        
"
m
"
        
"
"
        
"
f
"
        
"
v
"
        
"
"
        
"
g
"
        
"
b
"
        
"
"
        
"
"
        
"
z
"
        
"
h
"
        
"
"
        
"
j
"
    
]
    
"
Farsi
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Arabic
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Danish
"
:
[
        
"
e
"
        
"
r
"
        
"
n
"
        
"
t
"
        
"
a
"
        
"
i
"
        
"
s
"
        
"
d
"
        
"
l
"
        
"
o
"
        
"
g
"
        
"
m
"
        
"
k
"
        
"
f
"
        
"
v
"
        
"
u
"
        
"
b
"
        
"
h
"
        
"
p
"
        
"
"
        
"
y
"
        
"
"
        
"
"
        
"
c
"
        
"
j
"
        
"
w
"
    
]
    
"
Serbian
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
a
"
        
"
i
"
        
"
e
"
        
"
o
"
        
"
n
"
        
"
"
        
"
"
    
]
    
"
Lithuanian
"
:
[
        
"
i
"
        
"
a
"
        
"
s
"
        
"
o
"
        
"
r
"
        
"
e
"
        
"
t
"
        
"
n
"
        
"
u
"
        
"
k
"
        
"
m
"
        
"
l
"
        
"
p
"
        
"
v
"
        
"
d
"
        
"
j
"
        
"
g
"
        
"
"
        
"
b
"
        
"
y
"
        
"
"
        
"
"
        
"
"
        
"
c
"
        
"
"
        
"
"
    
]
    
"
Slovene
"
:
[
        
"
e
"
        
"
a
"
        
"
i
"
        
"
o
"
        
"
n
"
        
"
r
"
        
"
s
"
        
"
l
"
        
"
t
"
        
"
j
"
        
"
v
"
        
"
k
"
        
"
d
"
        
"
p
"
        
"
m
"
        
"
u
"
        
"
z
"
        
"
b
"
        
"
g
"
        
"
h
"
        
"
"
        
"
c
"
        
"
"
        
"
"
        
"
f
"
        
"
y
"
    
]
    
"
Slovak
"
:
[
        
"
o
"
        
"
a
"
        
"
e
"
        
"
n
"
        
"
i
"
        
"
r
"
        
"
v
"
        
"
t
"
        
"
s
"
        
"
l
"
        
"
k
"
        
"
d
"
        
"
m
"
        
"
p
"
        
"
u
"
        
"
c
"
        
"
h
"
        
"
j
"
        
"
b
"
        
"
z
"
        
"
"
        
"
y
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Hebrew
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Bulgarian
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Croatian
"
:
[
        
"
a
"
        
"
i
"
        
"
o
"
        
"
e
"
        
"
n
"
        
"
r
"
        
"
j
"
        
"
s
"
        
"
t
"
        
"
u
"
        
"
k
"
        
"
l
"
        
"
v
"
        
"
d
"
        
"
m
"
        
"
p
"
        
"
g
"
        
"
z
"
        
"
b
"
        
"
c
"
        
"
"
        
"
h
"
        
"
"
        
"
"
        
"
"
        
"
f
"
    
]
    
"
Hindi
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Estonian
"
:
[
        
"
a
"
        
"
i
"
        
"
e
"
        
"
s
"
        
"
t
"
        
"
l
"
        
"
u
"
        
"
n
"
        
"
o
"
        
"
k
"
        
"
r
"
        
"
d
"
        
"
m
"
        
"
v
"
        
"
g
"
        
"
p
"
        
"
j
"
        
"
h
"
        
"
"
        
"
b
"
        
"
"
        
"
"
        
"
f
"
        
"
c
"
        
"
"
        
"
y
"
    
]
    
"
Thai
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Greek
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Tamil
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
    
"
Kazakh
"
:
[
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
        
"
"
    
]
}
LANGUAGE_SUPPORTED_COUNT
:
int
=
len
(
FREQUENCIES
)
