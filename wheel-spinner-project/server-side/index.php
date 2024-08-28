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


<style>
.realistic-marker-highlight {
  position: relative;
  color: black; /* Ensure text color is readable over the highlight */
}

.realistic-marker-highlight:before {
  content: "";
  background-color: #ff6db7;
  width: 100%;
  height: 1em;
  position: absolute;
  z-index: -1;
  filter: url(#marker-shape);
  left: -0.25em;
  top: 0.1em;
  padding: 0 0.25em;
}
</style>

<svg xmlns="http://www.w3.org/2000/svg" version="1.1" class="svg-filters" style="display:none;">
  <defs>
    <filter id="marker-shape">
      <feTurbulence type="fractalNoise" baseFrequency="0 0.15" numOctaves="1" result="warp" />
      <feDisplacementMap xChannelSelector="R" yChannelSelector="G" scale="30" in="SourceGraphic" in2="warp" />
    </filter>
  </defs>
</svg>



<style>
 *{	margin:0;	padding:0; }

 @media (min-width: 768px) {
    #title h1 {
        font-size: 2rem;
    }

    #description p {
        font-size: 1.25rem;
    }
}

@media (max-width: 767px) {
    body {
        background: white !important;
        color: #000 !important; /* Adjust text color for readability on white background */

    }
    #title h1 {
    font-size: 2.5rem; /* Larger title font size */
    color: #000 !important; /* White color for better visibility */
    
}
#description p {
    color: #000 !important; 
}
}

#title h1, #description p, #result {
    text-align: center;
    margin: 20px 0;
    font-size: calc(10px + 1.5vmin); /* Adjust font size based on viewport */

}

#title h1 {
    font-size: 2.5rem; /* Larger title font size */
    color: #fff; /* White color for better visibility */
}

#description p {
    font-size: 1.2rem; /* Adjusted for better readability */
    font-weight: bold;
    color: #E0E0E0; /* Lighter color for text */
}

/* Result message styling */
#result {
    font-size: 1.2rem;
    font-weight: bold;
}
#description {
    text-align: center;
}



#result.congratulations {
    color: #ADFF2F; /* Bright green for success */
}

#result.message {
    color: #FFA07A; /* Lighter red for error messages, softer on dark backgrounds */
}

body{
    margin: 0;
    padding: 0;
    font-family: 'Exo 2', sans-serif;
    background: transparent;
    color: #fff;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
}

a{
	color:#34495e;	
}




/*WRAPPER*/
#wrapper{ 
    width: 90%;
    max-width: 600px; /* Adjust based on your preference */
    position:relative;
}

#txt{
	color:#eaeaea;	
}


/*WHEEL*/
#wheel{
	width:100%;
    max-width: 250px; 
	height:auto;
	border-radius:50%;	
    aspect-ratio: 1 / 1; 
    margin: 0 auto;
	position:relative;
	overflow:hidden;
	border:8px solid #fff;
    box-shadow: 0 0 20px #fff; /* White glow for prominence */
	transform: rotate(0deg);


}

#wheel:before{
	content:'';
	position:absolute;
	border:4px solid rgba(0,0,0,0.1);
	width:242px;
	height:242px;
	border-radius:50%;
	z-index:1000;	
}

#inner-wheel{
	width:100%;
	height:100%;
	
	-webkit-transition: all 6s cubic-bezier(0,.99,.44,.99);
	-moz-transition:    all 6 cubic-bezier(0,.99,.44,.99);
	-o-transition:      all 6s cubic-bezier(0,.99,.44,.99);
	-ms-transition:     all 6s cubic-bezier(0,.99,.44,.99);
	transition:         all 6s cubic-bezier(0,.99,.44,.99);	
}

#wheel div.sec{
	position: absolute;
	width: 0;
	height: 0;
	border-style: solid;
	border-width: 130px 75px 0;
	border-color: #19c transparent;
	transform-origin: 75px 129px;
	left:50px;
	top:-4px;	
	opacity:1;
}

#wheel div.sec:nth-child(1){
	transform: rotate(60deg);
	-webkit-transform: rotate(60deg);
	-moz-transform: rotate(60deg);
	-o-transform: rotate(60deg);
	-ms-transform: rotate(60deg);
	border-color: #16a085 transparent;	
}
#wheel div.sec:nth-child(2){
	transform: rotate(120deg);
	-webkit-transform: rotate(120deg);
	-moz-transform: rotate(120deg);
	-o-transform: rotate(120deg);
	-ms-transform: rotate(120deg);
	border-color: #2980b9 transparent;	
}
#wheel div.sec:nth-child(3){
	transform: rotate(180deg);
	-webkit-transform: rotate(180deg);
	-moz-transform: rotate(180deg);
	-o-transform: rotate(180deg);
	-ms-transform: rotate(180deg);
	border-color: #34495e transparent;	
}
#wheel div.sec:nth-child(4){
	transform: rotate(240deg);
	-webkit-transform: rotate(240deg);
	-moz-transform: rotate(240deg);
	-o-transform: rotate(240deg);
	-ms-transform: rotate(240deg);
	border-color: #f39c12 transparent;	
}
#wheel div.sec:nth-child(5){
	transform: rotate(300deg);
	-webkit-transform: rotate(300deg);
	-moz-transform: rotate(300deg);
	-o-transform: rotate(300deg);
	-ms-transform: rotate(300deg);
	border-color: #d35400 transparent;	
}
#wheel div.sec:nth-child(6){
	transform: rotate(360deg);
	-webkit-transform: rotate(360deg);
	-moz-transform: rotate(360deg);
	-o-transform: rotate(360deg);
	-ms-transform: rotate(360deg);
	border-color: #c0392b transparent;	
}


#wheel div.sec .fa{
	margin-top: -100px;
	color: rgba(0,0,0,0.2);
	position: relative;
	z-index: 10000000;
	display: block;
	text-align: center;
	font-size:36px;
	margin-left:-15px;
	
	text-shadow: rgba(255, 255, 255, 0.1) 0px -1px 0px, rgba(0, 0, 0, 0.2) 0px 1px 0px;
}




#spin{
	width:68px;
	height:68px;
	position:absolute;
	top:50%;
	left:50%;
	margin:-34px 0 0 -34px;
	border-radius:50%;
	box-shadow:rgba(0,0,0,0.1) 0px 3px 0px;
	z-index:1000;
	background: #6A5ACD;
	cursor:pointer;
	font-family: 'Exo 2', sans-serif;
	color: #FFF;

  -webkit-user-select: none; 
  -moz-user-select: none;    
  -ms-user-select: none;     
  -o-user-select: none;
  user-select: none;   
}


#spin:after{
	content:"SPIN";	
	text-align:center;
	line-height:68px;
	color:#CCC;
	text-shadow: 0 2px 0 #fff, 0 -2px 0 rgba(0,0,0,0.3) ;
	position: relative;
	z-index: 100000;
	width:68px;
	height:68px;
	display:block;
}

#spin:before{
	content:"";
	position:absolute;
	width: 0;
	height: 0;
	border-style: solid;
	border-width: 0 20px 28px 20px;
	border-color: transparent transparent #ffffff transparent;
	top:-12px;
	left:14px;
}

#inner-spin{
	width:54px;
	height:54px;
	position:absolute;
	top:50%;
	left:50%;
	margin:-27px 0 0 -27px;
	border-radius:50%;
	background:red;
	z-index:999;
	box-shadow:rgba(255,255,255,1) 0px -2px 0px inset, rgba(255,255,255,1) 0px 2px 0px inset,  rgba(0,0,0,0.4) 0px 0px 5px ;
	
	background: rgb(255,255,255); /* Old browsers */
	background: -moz-radial-gradient(center, ellipse cover,  rgba(255,255,255,1) 0%, rgba(234,234,234,1) 100%); /* FF3.6+ */
	background: -webkit-gradient(radial, center center, 0px, center center, 100%, color-stop(0%,rgba(255,255,255,1)), color-stop(100%,rgba(234,234,234,1))); /* Chrome,Safari4+ */
	background: -webkit-radial-gradient(center, ellipse cover,  rgba(255,255,255,1) 0%,rgba(234,234,234,1) 100%); /* Chrome10+,Safari5.1+ */
	background: -o-radial-gradient(center, ellipse cover,  rgba(255,255,255,1) 0%,rgba(234,234,234,1) 100%); /* Opera 12+ */
	background: -ms-radial-gradient(center, ellipse cover,  rgba(255,255,255,1) 0%,rgba(234,234,234,1) 100%); /* IE10+ */
	background: radial-gradient(ellipse at center,  rgba(255,255,255,1) 0%,rgba(234,234,234,1) 100%); /* W3C */
	filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#ffffff', endColorstr='#eaeaea',GradientType=1 ); /* IE6-9 fallback on horizontal gradient */	
}

#spin:active #inner-spin{
	box-shadow:rgba(0,0,0,0.4) 0px 0px 5px inset;
}

#spin:active:after{
	font-size:15px;	
}



#shine{
	width:250px;
	height:250px;
	position:absolute;
	top:0;
	left:0;
	background: -moz-radial-gradient(center, ellipse cover,  rgba(255,255,255,1) 0%, rgba(255,255,255,0.99) 1%, rgba(255,255,255,0.91) 9%, rgba(255,255,255,0) 100%); /* FF3.6+ */
background: -webkit-gradient(radial, center center, 0px, center center, 100%, color-stop(0%,rgba(255,255,255,1)), color-stop(1%,rgba(255,255,255,0.99)), color-stop(9%,rgba(255,255,255,0.91)), color-stop(100%,rgba(255,255,255,0))); /* Chrome,Safari4+ */
background: -webkit-radial-gradient(center, ellipse cover,  rgba(255,255,255,1) 0%,rgba(255,255,255,0.99) 1%,rgba(255,255,255,0.91) 9%,rgba(255,255,255,0) 100%); /* Chrome10+,Safari5.1+ */
background: -o-radial-gradient(center, ellipse cover,  rgba(255,255,255,1) 0%,rgba(255,255,255,0.99) 1%,rgba(255,255,255,0.91) 9%,rgba(255,255,255,0) 100%); /* Opera 12+ */
background: -ms-radial-gradient(center, ellipse cover,  rgba(255,255,255,1) 0%,rgba(255,255,255,0.99) 1%,rgba(255,255,255,0.91) 9%,rgba(255,255,255,0) 100%); /* IE10+ */
background: radial-gradient(ellipse at center,  rgba(255,255,255,1) 0%,rgba(255,255,255,0.99) 1%,rgba(255,255,255,0.91) 9%,rgba(255,255,255,0) 100%); /* W3C */
filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#ffffff', endColorstr='#00ffffff',GradientType=1 ); /* IE6-9 fallback on horizontal gradient */


opacity:0.2;
	
}



/*ANIMATION*/
@-webkit-keyframes hh {
  0%, 100%{
    transform: rotate(0deg);
    -webkit-transform: rotate(0deg);
  }

  50%{
    transform: rotate(7deg);
    -webkit-transform: rotate(7deg);
  }
}

@keyframes hh {
   0%, 100%{
    transform: rotate(0deg);
    -webkit-transform: rotate(0deg);
  }

  50%{
    transform: rotate(7deg);
    -webkit-transform: rotate(7deg);
  }
}

.spin {
  -webkit-animation: hh 0.1s; /* Chrome, Safari, Opera */
    animation: hh 0.1s;
}
      </style>