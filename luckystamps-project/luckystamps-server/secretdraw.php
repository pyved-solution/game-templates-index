<?php


// WARNING: cannot use more than a single null value or the algorithm will fail
$weights = [
    
    1 => 0.11,
    2 => 0.13,
    3 => 0.13,
    4 => 0.13,
    5 => 0.14,
    6 => 0.14,
    7 => 0.17,
0 => 0.02,
-1 => 0.03
];


function draw_a_stamp(){
	global $weights;

	// Let's compute the total sum of non-null weights
	$specified_total = array_sum(array_filter($weights, function($weight) {
		return $weight !== null;
	}));

	// Computing the total sum by substituting a "null" if it has been found
	$total = $specified_total;
	foreach ($weights as $key => $weight) {
		if ($weight === null) {
			$weights[$key] = 1.0 - $specified_total;
			$total = 1.0;  // After assigning the remaining weight, total must be 1.0
		}
	}

	// Check if the total sum is equal to 1.0
	if (abs(array_sum($weights) - 1.0) > 1e-6) {
		throw new Exception('The sum of all weights does not equal 1.0');
	}

	// Perform the "tirage"
	$rand = mt_rand(1, $total * 1000000) / 1000000; // Normalized to a floating point number
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
