![nanobrd](https://gitlab.com/ParlorTricks/nanobrd/-/raw/main/nanobrd-opt.gif)

_GIF compressed with gifsicle_

This is a direct translation of daves84 [nanobrd](https://daves84.itch.io/nanobrd) in Lua to Fennel. You can find the [cart on tic80.com](http://tic80.com/play?cart=2820) and the code is supplied below.

I have tried to make this as Fennel(ish) as possible while still staying true to what daves84 coded. I have run [fnlfmt](https://git.sr.ht/~technomancy/fnlfmt) and [check.fnl](https://github.com/dokutan/check.fnl) against it to clean up any obvious mistakes.

You can also find the source code for both Lua and Fennel hosted at [https://gitlab.com/ParlorTricks/nanobrd](https://gitlab.com/ParlorTricks/nanobrd)

```fennel
;; title:   nanobrd
;; author:  parlortricks
;; desc:    fennel conversion of daves84 nanobrd
;; site:    https://daves84.itch.io/nanobrd
;; license: MIT
;; SPDX-License-Identifier: MIT
;; version: 1.0
;; script:  fennel
;; strict:  true
;; input: gamepad
;; saveid: nanobrd-1

(var (a t z p w s) (values 60 0 0 0 240 math.sin))
(var y a)

(fn _G.TIC []
  (cls)
  (when (btn 4)
    (set z 3)
    (sfx 0 0))
  (when (> z (- 3))
    (set z (- z 0.5)))
  (set y (- y z))
  (for [i 0 4 1]
    (rect (% (+ (- w (/ t 2)) (* i a)) w) 0 10 136 2)
    (rect (% (+ (- w (/ t 2)) (* i a)) w) (+ 40 (* 30 (s i))) 10 30 0))
  (when (or (or (= (pix 20 y) 2) (> y 136)) (< y 0))
    (set y a)
    (set t 0))
  (print (.. "nanobrd " (// t 120)) 0 0 12)
  (for [x 0 w]
    (for [y 0 136]
      (pix x y (+ (+ (+ (pix x y) (s (/ (+ x t) a))) (s (/ y a)))
                  (s (bxor x y))))))
  (circ 20 y 2 12)
  (sfx 0 (math.floor (/ y 3)))
  (set t (+ t 1)))
```

_This translation was done with daves84 permission_