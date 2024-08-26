<?php

function std_curl_call($maUrl,$follow_redir=false){
    // Initialize cURL session
	
	// -- debug
	// echo 'je call cette URL la:';
	// echo $maUrl;
	
	if (!$follow_redir){
		//default way of doing
		    $ch = curl_init($maUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPGET, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
    ]);
	 $response = curl_exec($ch);
	} else{
		// that way of doing is important too, because when we call an endpoint that is auto-reconnected
		// in https the default way of doing wont work!
		$ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $maUrl, // Set the endpoint URL
        CURLOPT_RETURNTRANSFER => true, // Return response as a string
        CURLOPT_FOLLOWLOCATION => true, // Follow redirects if any
        CURLOPT_MAXREDIRS => 10, // Limit the number of redirects
        CURLOPT_TIMEOUT => 30, // Set the maximum execution time for the cURL session
        CURLOPT_HTTPGET => true, // Use HTTP GET method
        CURLOPT_SSL_VERIFYPEER => false, // Disable SSL verification (only for testing)
    ]);
    $response = curl_exec($ch);
	}
   
	$http_code = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    if ($response === false || !($http_code == 200 ))  {   //|| $http_code == 301))
        throw new Exception("curl:".curl_error($ch)." / resp=".$response . "http code:".$http_code);
    }
    curl_close($ch);

    $rez = json_decode($response, true);  // true means make it associative array
	if ($rez==null){
		echo 'received data='.$response.' /// ERR='. json_last_error();
		throw new Exception('json error!');
	}
	return $rez;
}
