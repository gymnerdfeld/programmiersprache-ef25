; ==== ;
; Math ;
; ==== ;
(sto square (func (x)
    (* x x)
))

(sto sqrt (func (x)
    (** x 0.5)
))

(sto e 2.718281828459045)
(sto pi 3.141592653589793)
(sto tau (* 2 pi))


; ==================== ;
; Logik und Vergleiche ;
; ==================== ;
(sto not (func (x)
    (if x False True)
))

(sto > (func (x y)
    (< y x)
))

(sto >= (func (x y)
    (not (< x y))
))

(sto <= (func (x y)
    (not (> x y))
))

(sto == (func (x y)
    (if (< x y)
        False
        (if (< y x)
            False
            True
        )
    )
))

(sto != (func (x y) 
    (not (== x y))
))


; ======================= ;
; Experiment mit Closures ;
; ======================= ;
(sto make_adder (func (x) (begin
    (sto inner (func (y)
        (+ x y)
    ))
    inner
)))
(sto plus5 (make_adder 5))


; =========================== ;
; Langsame Fibonacci-Funktion ;
; =========================== ;
(sto fib (func (n)
    (if (< n 2)
        1
        (+
            (fib (- n 1)) 
            (fib (- n 2))
        )
    )
))


; =================================================== ;
; Resultate einer Funktion zwischenspeichern (cachen) ;
; =================================================== ;
(sto cached (func (f) (begin
    (sto cache (dict-new))
    (func (x)
        (if (dict-in? cache x)
            (dict-get cache x)
            (begin
                (sto result (f x))
                (dict-set cache x result)
                result
            )
        )
    )
)))


; ================================ ;
; Beschleunigte Fibonacci-Funktion
; ================================ ;
(sto fib (cached fib))


; =============== ;
; Zahlenratespiel ;
; =============== ;
(sto guesser-game (func () (begin
    (sto number (// (* (random) 100) 1))

    (sto data (dict-new))
    (sto versuche-key 234)
    (dict-set data versuche-key 0)

    (sto guesser-func (func (x)
        (if (== x -1)
            (dict-get data versuche-key)
            (if (== x number)
                (string Du hast die zahl gefunden!)
                (begin
                    (dict-set data versuche-key (+ (dict-get data versuche-key) 1))
                    (if (< x number)
                        (string Zu klein)
                        (string Zu gross)
                    )
                )
            )
        )
    ))
    guesser-func
)))
