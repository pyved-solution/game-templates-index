<?php

function getUserIdByJwt($jwt) {
    // JWT token to be sent in the API call

    // API endpoint URL
    $endpoint = "https://t-api-beta.kata.games/user/jwt?jwt=" . urlencode($jwt);

    // Initialize cURL session
    $curl = curl_init();

    // Set cURL options
    curl_setopt_array($curl, [
        CURLOPT_URL => $endpoint, // Set the endpoint URL
        CURLOPT_RETURNTRANSFER => true, // Return response as a string
        CURLOPT_FOLLOWLOCATION => true, // Follow redirects if any
        CURLOPT_MAXREDIRS => 10, // Limit the number of redirects
        CURLOPT_TIMEOUT => 30, // Set the maximum execution time for the cURL session
        CURLOPT_HTTPGET => true, // Use HTTP GET method
        CURLOPT_SSL_VERIFYPEER => false, // Disable SSL verification (only for testing)
    ]);

    // Execute the cURL session
    $response = curl_exec($curl);

    // Check for errors
    if (curl_errno($curl)) {
        $error_message = curl_error($curl);
        // Handle cURL error
        echo "Error: $error_message";
        return null;
    } else {
        // API call successful
        $http_status_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        if ($http_status_code === 200) {
            // Parse and process the API response
            $data = json_decode($response, true);
            // Access the user_id from the response
            $user_id = $data['user_id'];
            // Return the user ID
            return $user_id;
        } else {
            // Handle non-200 HTTP response
            echo "HTTP Error: $http_status_code";
            return null;
        }
    }

    // Close cURL session
    curl_close($curl);
}
if(isset($_REQUEST['jwt'])) {
    $token = $_REQUEST['jwt'];

    $userId = getUserIdByJwt($token);
    $gamePrice = 5; 

    // Send parameters as part of the URL 
    $url = 'https://' . $_SERVER['HTTP_HOST'] . '/lucky-stamps/testluck.php';
    $params = http_build_query(['user_id' => $userId, 'game_price' => $gamePrice, 'token' => $token]);
    // $jsonObj = json_decode(file_get_contents($url . '?' . $params), true);
    header('Content-Type: application/json');

    echo file_get_contents($url . '?' . $params);
} else {
    echo 'No jwt sent';
}
