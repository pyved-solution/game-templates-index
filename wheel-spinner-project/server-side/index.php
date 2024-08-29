<script src="https://t-api-beta.kata.games/integration/connectorV.js"></script>

<head>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>

<link href="//maxcdn.bootstrapcdn.com/font-awesome/4.1.0/css/font-awesome.min.css" rel="stylesheet">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<div id="title">
    <h1>🎉 Welcome to Luck Spinner! 🎉</h1>
</div>
<div id="description">
	<p>Here's how it works:</p>
	<p>🌀 Spin daily for FREE! One guaranteed spin, two spins if you're lucky</p>
	<p>🎯 1 in 36 chance for a jackpot of 500 credits! Get the trophy symbol twice to trigger the jackpot</p>
	<p>💸 a 14% chance for a minor prize of 10 credits! If you get the trophy symbol once.</p>
	<p>Play now and let the fun begin! 🌟</p>

</div>
<div id="wrapper">
    <div id="wheel">
        <div id="inner-wheel">
            <div class="sec"><span class="fa fa-times lose"></span></div>
            <div class="sec"><span class="fa fa-times lose"></span></div>
            <div class="sec"><span class="fa fa-times lose"></span></div>
            <div class="sec"><span class="fa fa-trophy win"></span></div>
            <div class="sec"><span class="fa fa-times lose"></span></div>
            <div class="sec"><span class="fa fa-times lose"></span></div>
        </div>

        <div id="spin">
            <div id="inner-spin"></div>
        </div>

        <div id="shine"></div>
    </div>
    </div>

    <div id="result">
        <!-- Result message will be displayed here -->
    </div>
    <script>
        let jwt = undefined
window.addEventListener('message', function(event) {
    console.log('message received')
    if (event.origin !== 'https://beta.kata.games') return;

    var receivedData = event.data;
    jwt = receivedData
});
</script>
<script>
let clicks = 0; // Define clicks here so it's accessible globally
let startingDegree = 0; // Variable to store the starting degree
let isSpinning = false; // Track if the wheel is currently spinning
let isFirstSpin = true; // Track if it's the first spin
let spinData = null; // Store spin data from the API


function getResetCountdown() {
    let resetTime = getResetTime();
    let now = new Date();
    let timeLeft = resetTime - now;
    let hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    let minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    let seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
    return hours + "h " + minutes + "m " + seconds + "s";
}

function performSpin(isWin, isSecondSpin = false) {
    isSpinning = true;
    $('#spin').prop('disabled', true);

    let extraDegree = Math.floor(Math.random() * (720 - 360 + 1)) + 360;

    let loseDegrees = [300, 600, 900, 1500, 1800];
    let winDegrees = [1200];

    let targetArray = isWin ? winDegrees : loseDegrees;
    let targetDegree = targetArray[Math.floor(Math.random() * targetArray.length)];

    let currentRotation = $('#inner-wheel').data('rotation') || 0;
    let adjustment = targetDegree - (currentRotation + extraDegree) % 360;

    if (adjustment < 0) {
        adjustment += 360;
    }

    let totalDegree = extraDegree + adjustment;

    $('#inner-wheel').css({
        'transition': 'transform 3s ease-in-out',
        'transform': 'rotate(' + (currentRotation + totalDegree) + 'deg)'
    });

    $('#inner-wheel').data('rotation', currentRotation + totalDegree);

    let countdownInterval; // Declare the countdown interval variable outside

    setTimeout(() => {
        $('#inner-wheel').css({'transition': 'none'});
        isSpinning = false;
        $('#spin').prop('disabled', false);

        if (!isSecondSpin) {
            if (!isWin) {
                displayMessage("This isn't your lucky day... Try again in: " + getResetCountdown(), 'error');
                countdownInterval = setInterval(() => {
                    displayMessage("This isn't your lucky day... Try again in: " + getResetCountdown(), 'error');
                }, 1000); // Start countdown interval only for first spin if lost
            } else {
                displayMessageHTML("<span class=\"realistic-marker-highlight\">You're close!</span> You've already won <span class=\"realistic-marker-highlight\">10 Credits!</span> Spin again for a chance at the jackpot.", 'info');
            }
        } else {
            clearInterval(countdownInterval); // Clear interval if it's the second spin
            if (spinData.wonSecond) {
                displayMessageHTML("Congratulations, you won the jackpot and earned a total of 500 credits!", 'congratulations');
            } else {
                displayMessageHTML("<span class=\"realistic-marker-highlight\">You've won 10 credits</span> but missed the jackpot. <br> Try your luck in : " + getResetCountdown(), 'info');
                countdownInterval = setInterval(() => {
                    displayMessageHTML("<span class=\"realistic-marker-highlight\">You've won 10 credits</span> but missed the jackpot. <br> Try your luck in : " + getResetCountdown(), 'info');
                }, 1000); // Start countdown interval only for first spin if lost
            }
            isFirstSpin = true;
            $('#spin').prop('disabled', true);
        }
    }, 3000);
}



function spin() {
    if (isSpinning || jwt === null) return; // Prevent spinning if already spinning or user not logged in

    if (isFirstSpin) {
        $.ajax({
            url: './wheel.php',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ jwt: jwt }),
            success: function(response) {
                spinData = JSON.parse(response);
                if (!spinData.success) {
                	displayMessageHTML('<span class="realistic-marker-highlight">'+spinData.message+'</span>', 'error');
                    //displayMessage(spinData.message, 'error');
                    return;
                }

                performSpin(spinData.wonFirst);
                isFirstSpin = !spinData.wonFirst; // Only allow second spin if first was won
            },
        error: function(xhr, textStatus, errorThrown) {
            var responseJSON = JSON.parse(xhr.responseText);
            if (responseJSON && responseJSON.message) {
                displayMessageHTML('<span class="realistic-marker-highlight">'+responseJSON.message+'</span>', 'error');
            } else {
                displayMessage("An error occurred, please try again later.", 'error');
            }
            $('#spin').prop('disabled', false); // Re-enable button on error
        }
        });
    } else {
        // Handle second spin without a new API call
        performSpin(spinData.wonSecond, true);
    }
}

$(document).ready(function() {
    $('#spin').click(spin);
    
});

function displayMessage(message, className) {
    $('#result').text(message).removeClass().addClass(className);
}
function displayMessageHTML(message, className) {
    $('#result').html(message).removeClass().addClass(className);
}

function getResetTime() {
    const now = new Date();
    let resetTime = new Date();
    resetTime.setUTCHours(22, 0, 0, 0); // Réinitialisation à 22:00 UTC (minuit heure de Paris)
    resetTime.setUTCHours(resetTime.getUTCHours() + 2); // Ajouter 2 heures pour Paris
    resetTime.setUTCMinutes(0);
    resetTime.setUTCSeconds(0);
    resetTime.setUTCMilliseconds(0);

    // Si l'heure actuelle est postérieure à l'heure de réinitialisation, ajoutez un jour pour la prochaine réinitialisation
    if (now.getTime() > resetTime.getTime()) {
        resetTime.setDate(resetTime.getDate() + 1);
    }

    return resetTime;
}

</script>

<link rel="stylesheet" href="wheel_game.css">
