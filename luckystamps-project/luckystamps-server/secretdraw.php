<?php

function draw_a_stamp() {
	$weights = [
        -1 => 8, // 8% chance
        0 => 1,  // 1% chance
    ];
    for ($i = 1; $i <= 7; $i++) {
        $weights[$i] = 91 / 7;
    }
    $total = array_sum($weights);
    $rand = mt_rand(1, $total);
    foreach ($weights as $number => $weight) {
        if ($rand <= $weight) return $number;
        $rand -= $weight;
    }
}


if ( basename(__FILE__) == basename($_SERVER['SCRIPT_FILENAME']) ) { //is called directly

    $result = draw_a_stamp();
    header('Content-Type: application/json');
    echo json_encode(["stamp"=>$result]);
}
