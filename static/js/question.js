$(function() {

    const time = document.getElementById("time").getAttribute('data-value');
    const timerDiv = document.getElementById("timer");
    const csrf = document.getElementsByName('csrfmiddlewaretoken');
    const data = {}
    const performance = window.performance.getEntriesByType('navigation').map((nav) => nav.type);
    const pageActions = ['reload', 'back_forward', 'navigate'];
    data['csrfmiddlewaretoken'] = csrf[0].value
    let displaySec
    let displayMin
    const zeroTimer = document.getElementById("zero-timer");

    console.log(zeroTimer);

    // $("#answer-form").submit(function() {
    //     $(this).find(':input[type=submit]').prop('disabled', true);
    //     localStorage.removeItem("remainingSec");
    //     localStorage.removeItem("remainingMin");
    // });

    const timeStart = (time) => {
        if (!(localStorage.getItem("remainingSec")) && !(localStorage.getItem("remainingMin")) && (time.toString().length < 2)) {
            timerDiv.innerHTML = `<h4><b>0${time}:00</b></h4>`
        } else if (!(localStorage.getItem("remainingSec")) && !(localStorage.getItem("remainingMin")) && (time.toString().length >= 2)){
            timerDiv.innerHTML = `<h4><b>${time}:00</b></h4>`
        }
        let initialMinutes = time - 1
        let initialSeconds = 60
        let seconds = localStorage.getItem("remainingSec") || initialSeconds;
        let minutes = localStorage.getItem("remainingMin") || initialMinutes;

        const timer = setInterval(()=>{
            seconds --
            localStorage.setItem("remainingSec", seconds)
            if (seconds < 0) {
                seconds = 59
                minutes --
                localStorage.setItem("remainingMin", minutes)
            }
            if (minutes.toString().length < 2) {
                displayMin = '0' + minutes
            } else {
                displayMin = minutes
            }
            if (seconds.toString().length < 2) {
                displaySec = '0' + seconds
            } else {
                displaySec = seconds
            }
            if (minutes == 0 && seconds == 0) {
                timerDiv.innerHTML = `<h4><b>00:00</b></h4>`
                clearInterval(timer);
                localStorage.removeItem("remainingSec");
                localStorage.removeItem("remainingMin");
                $("#answer-form").submit();
            }

            if (zeroTimer.innerHTML == 1) {
                timerDiv.innerHTML = `<h4><b>00:00</b></h4>`
                clearInterval(timer);
                localStorage.removeItem("remainingSec");
                localStorage.removeItem("remainingMin");
            } else {
                timerDiv.innerHTML = `<h4><b>${displayMin}:${displaySec}</b></h4>`
            }

        }, 1000)

    };

    timeStart(time);

    // refreshes timer when page reloaded
    if (pageActions.includes(performance[0])) {
        localStorage.removeItem("remainingSec");
        localStorage.removeItem("remainingMin");
        timeStart(time);
    };


});
