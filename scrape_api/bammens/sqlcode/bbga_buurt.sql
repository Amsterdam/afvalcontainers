UPDATE kilogram_buurtfractiestatweek s
	set inhabitants=b.inhabitants
from buurt_counts b
WHERE b.buurt_code = s.buurt_code
AND b."year" = s."year";

UPDATE kilogram_buurtfractiestatmonth s
	set inhabitants=b.inhabitants
from buurt_counts b
WHERE b.buurt_code = s.buurt_code
AND b."year" = s."year";


/*
UPDATE kilogram_buurtfractiestatmonth

*/
