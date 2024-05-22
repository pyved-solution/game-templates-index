<?php

function filterLatestDataEntries($data) {
    $latestData = [];
    foreach ($data as $entry) {
        $generation = $entry[0];
        $column = $entry[1];
        // The key is a combination of generation and column to ensure uniqueness
        $latestData[$generation . '_' . $column] = $entry;
    }
    // Convert the associative array back to an indexed array with only the latest entries
    return array_values($latestData);
}

function compute_credit_gains($data, $rows, $columns) {
	$rewards = [
	1 => 10,
	2 => 10,
	3 => 10,
	4 => 10,
	5 => 10,
	6 => 10,
	7 => 10,
	8 => 10
	];

    $filteredData = filterLatestDataEntries($data);
    $maxGeneration = max(array_map(function ($entry) {
        return $entry[0];
    }, $filteredData));
    $generations = $maxGeneration + 1;
    
    $creditsPerGeneration = array_fill(0, $generations, 0);

    // Prepare a structured array to make horizontal and vertical checks easier
    $structuredData = [];
    foreach ($filteredData as $entry) {
        $generation = $entry[0];
        $column = substr($entry[1], 1);
        if (!isset($structuredData[$generation])) {
            $structuredData[$generation] = array_fill(0, $columns, array_fill(0, $rows, null));
        }
        for ($i = 0; $i < $rows; $i++) {
            $structuredData[$generation][$column][$i] = $entry[$i + 2];
        }
    }

    // Check for horizontal matches
    foreach ($structuredData as $generation => $grid) {
        for ($row = 0; $row < $rows; $row++) {
            for ($col = 0; $col <= $columns - 3; $col++) { // Adjust loop to check up to the third-last column
				$elt_type = $grid[$col][$row];
                if ($grid[$col][$row] === $grid[$col + 1][$row] && $grid[$col][$row] === $grid[$col + 2][$row]) {
                    // Found a horizontal match of 3
                    $creditsPerGeneration[$generation] += $rewards[$elt_type] ;
                    // Skip the next two cells in the row to avoid counting a sequence of 4 or more more than once
                    $col += 2;
                }
            }
        }
    }

    // Check for vertical matches
    for ($col = 0; $col < $columns; $col++) {
        for ($generation = 0; $generation < $generations; $generation++) {
            for ($row = 0; $row <= $rows - 3; $row++) {
                if ($structuredData[$generation][$col][$row] === $structuredData[$generation][$col][$row + 1] && $structuredData[$generation][$col][$row] === $structuredData[$generation][$col][$row + 2]) {
                    // Found a vertical match of 3
                    $creditsPerGeneration[$generation] += 10;
                    // Skip the next two cells in the column to avoid counting a sequence of 4 or more more than once
                    $row += 2;
                }
            }
        }
    }

    return $creditsPerGeneration;
}

// Check if the script is being included or called directly via GET

if ( basename(__FILE__) == basename($_SERVER['SCRIPT_FILENAME']) ) {  // called directly!
	
    $result = compute_credit_gains(
		json_decode($_GET['data']),
		3, 5
	);
    // Set headers to indicate JSON content
    header('Content-Type: application/json');
	// et voila
    echo json_encode(["gains"=>$result]);
}
