SELECT benefit, pr0, pr1, spid0, spid1, symbol_id, ask from LATERAL(
    SELECT (maxim-leas)*100/leas benefit, * FROM LATERAL(
        SELECT
            GREATEST(s0.price, s1.price) maxim,
            LEAST(s0.price, s1.price) leas,
            s0.spot_id spid0, s1.spot_id spid1,
            s0.price pr0, s1.price pr1,
            s0.ask ask,
            s0.symbol_id symbol_id
            FROM spot s0
            INNER JOIN spot s1 ON s0.spot_id < s1.spot_id
            AND s0.symbol_id = s1.symbol_id
            AND s0.ask = s1.ask)
    X0) X1 WHERE benefit > .5;