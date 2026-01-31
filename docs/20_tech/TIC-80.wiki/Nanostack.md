![nanostack](https://gitlab.com/ParlorTricks/nanostack/-/raw/main/nanostack-opt.gif)

_GIF compressed with gifsicle_

This is a direct translation of daves84 [nanostack](https://daves84.itch.io/nanostack) in Lua to Fennel. You can find the [cart on tic80.com](http://tic80.com/play?cart=2821) and the code is supplied below.

I have tried to make this as Fennel(ish) as possible while still staying true to what daves84 coded. I have run [fnlfmt](https://git.sr.ht/~technomancy/fnlfmt) and [check.fnl](https://github.com/dokutan/check.fnl) against it to clean up any obvious mistakes.

You can also find the source code for both Lua and Fennel hosted at [https://gitlab.com/ParlorTricks/nanostack](https://gitlab.com/ParlorTricks/nanostack)

```fennel
;; title:   nanostack
;; author:  parlortricks
;; desc:    fennel conversion of daves84 nanostack
;; site:    https://daves84.itch.io/nanostack
;; license: MIT
;; SPDX-License-Identifier: MIT
;; version: 1.0
;; script:  fennel
;; strict:  true
;; input: gamepad
;; saveid: nanostack-1

(var (t x w c s u v) (values 0 0 30 1 0.5 {} {}))

(fn _G.TIC []
  (cls 10)
  (rect 0 126 240 10 14)
  (for [i 1 (length u) 1]
    (for [j 1 8 1]
      (rect (+ (. u i) (* j 3)) (- 126 (* i 10)) (- (- 70 (* i 5)) (* j 6)) 10
            (- 17 j))))
  (for [j 1 8 1]
    (rect (+ (% x 240) (* j 3)) (- 126 (* c 10)) (- (- 70 (* c 5)) (* j 6)) 10
          (- 17 j)))
  (when (> (btnp) 0)
    (set t 0)
    (for [i (% x 240) (- (+ (% x 240) 70) (* c 5)) 1]
      (when (not= (pix i (+ (- 126 (* c 10)) 10)) 10)
        (set t 1)))
    (if (and (= t 0) (> c 1))
        (do
          (set u {})
          (set c 1)
          (set x 0))
        (do
          (tset u c (% x 240))
          (set c (+ c 1))
          (set x 0))))
  (when (= c 13)
    (set u {})
    (set c 1)
    (set x 0)
    (set s (+ s 0.5)))
  (print (.. "Level " (math.floor (/ s 0.5))))
  (set x (+ x s))
  (set t (+ t 1)))
```

_This translation was done with daves84 permission_