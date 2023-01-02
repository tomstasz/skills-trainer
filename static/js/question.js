$(function() {

    const time = document.getElementById("time").getAttribute('data-value');
    const timerDiv = document.getElementById("timer");
    const csrf = document.getElementsByName('csrfmiddlewaretoken');
    const data = {}
    data['csrfmiddlewaretoken'] = csrf[0].value
    let displaySec
    let displayMin


    $("#question-form").submit(function() {
        $(this).find(':input[type=submit]').prop('disabled', true);
        localStorage.removeItem("remainingSec");
        localStorage.removeItem("remainingMin");
    });

    const timeStart = (time) => {
        if (!(localStorage.getItem("remainingSec")) && !(localStorage.getItem("remainingMin")) && (time.toString().length < 2)) {
            timerDiv.innerHTML = `<b>0${time}:00</b>`;
        } else if (!(localStorage.getItem("remainingSec")) && !(localStorage.getItem("remainingMin")) && (time.toString().length >= 2)){
            timerDiv.innerHTML = `<b>${time}:00</b>`
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
                timerDiv.innerHTML = "<b>00:00</b>"
                clearInterval(timer);
                localStorage.removeItem("remainingSec");
                localStorage.removeItem("remainingMin");
                $("#question-form").submit();
            }

            window.onpageshow = function (event) {
                if (event.persisted) {
                    timerDiv.innerHTML = "<b>00:00</b>"
                    clearInterval(timer);
                    localStorage.removeItem("remainingSec");
                    localStorage.removeItem("remainingMin");
                    window.history.forward();
                    $("#question-form").submit();
                }
            };
            timerDiv.innerHTML = `<b>${displayMin}:${displaySec}</b>`
        }, 1000)

    };

    timeStart(time);



});
