document.addEventListener("DOMContentLoaded", function () {

const resultsDiv = document.getElementById('results');
const wrapper = document.getElementsByClassName('row-wrapper');
const training = document.getElementById('training');


function setCanvas(key, row, prefix) {
    let col = document.createElement('div');
    col.classList.add("col");
    row.appendChild(col);
    let chartDiv = document.createElement('div');
    chartDiv.classList.add('chart', 'w-75', 'd-inline-block', "h-25");
    col.appendChild(chartDiv);
    let canv = document.createElement('canvas');
    // For some raeson js has a problem with pluses in the string
    if(key == "C++") {
        canv.setAttribute('id', `${prefix.toLowerCase()}-chart-c-plus`);
    } else {
        canv.setAttribute('id', `${prefix.toLowerCase()}-chart-${key.toLowerCase()}`);
    }
    canv.setAttribute('height', '300px');
    canv.classList.add("chart-canvas");
    chartDiv.appendChild(canv);
};



if (resultsDiv != null) {
    let result = JSON.parse(resultsDiv.getAttribute('data-results'));

    for (let key in result) {
        let row = document.createElement('div');
        row.classList.add("row");
        wrapper[0].appendChild(row);
        let title = document.createElement('h3');
        let seniority = document.createElement('h3');
        if (training) {
            title.innerHTML = key;
            if (result[key]["seniority"] == 1) {
                seniority.innerHTML = "Junior";
            } else if (result[key]["seniority"] == 2) {
                seniority.innerHTML = "Regular";
            } else if (result[key]["seniority"] == 3) {
                seniority.innerHTML = "Senior";
            }
        };
        row.appendChild(title);
        title.append(seniority)
        setCanvas(key, row, "result");
        setCanvas(key, row, "questions");
    };

    if (training) {

        const BarsChart = (function() {

            for (let key in result) {
                var $chartAnswersCanvas = $(`#result-chart-${key.toLowerCase()}`);
                var $chartQuestionsCanvas = $(`#questions-chart-${key.toLowerCase()}`);

                if (key == "C++") {
                    var $chartAnswersCanvas = $('#result-chart-c-plus');
                    var $chartQuestionsCanvas = $('#questions-chart-c-plus');
                } else {
                    var $chartAnswersCanvas = $(`#result-chart-${key.toLowerCase()}`);
                    var $chartQuestionsCanvas = $(`#questions-chart-${key.toLowerCase()}`);
                }

                function initChartAnswers($chartAnswersCanvas) {

                    // Create chart
                    const answerChart = new Chart($chartAnswersCanvas, {
                        type: 'bar',
                        options: {
                            scales: {
                                yAxes: [{
                                    display: true,
                                    ticks: {
                                        suggestedMin: 0,
                                        suggestedMax: 100,
                                    },
                                }],
                                xAxes: [{
                                    display: true,
                                    barPercentage: 0.2,
                                }]
                            },
                        },
                        data: {
                            labels: [],
                            datasets: [{
                                label: '% of correct answers',
                                data: [],
                                backgroundColor: [],
                            }],
                        },
                    });


                    if ("junior_score" in result[key]) {
                        answerChart.data.datasets[0]["data"].push(result[key]["junior_score"]);
                        answerChart.data.labels.push("Junior");
                    };

                    if ("regular_score" in result[key]) {
                        answerChart.data.datasets[0]["data"].push(result[key]["regular_score"]);
                        answerChart.data.labels.push("Regular");
                    };

                    if ("senior_score" in result[key]) {
                        answerChart.data.datasets[0]["data"].push(result[key]["senior_score"]);
                        answerChart.data.labels.push("Senior");
                    };

                    answerChart.data.datasets[0]["data"].push(result[key]["general_score"]);
                    answerChart.data.labels.push("General");

                    for (data in result[key]) {
                        if (data.endsWith("score")) {
                            answerChart.data.datasets[0]["backgroundColor"].push('#FFA500');
                        }
                    };
                    answerChart.update();


                    // Save to jQuery object
                    $chartAnswersCanvas.data('chart', answerChart);

                };


                function initChartQuestions($chartQuestionsCanvas) {

                    // Create chart
                    const questionsChart = new Chart($chartQuestionsCanvas, {
                        type: 'bar',
                        options: {
                            scales: {
                                yAxes: [{
                                    display: true,
                                    ticks: {
                                        suggestedMin: 0,
                                        suggestedMax: 12,
                                    },
                                }],
                                xAxes: [{
                                    display: true,
                                    barPercentage: 0.2,
                                }]
                            },
                        },
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'number of asked questions',
                                data: [],
                                backgroundColor: [],
                            }],
                        },
                    });


                    if ("junior_questions" in result[key]) {
                        questionsChart.data.datasets[0]["data"].push(result[key]["junior_questions"]);
                        questionsChart.data.labels.push("Junior");
                    };

                    if ("regular_questions" in result[key]) {
                        questionsChart.data.datasets[0]["data"].push(result[key]["regular_questions"]);
                        questionsChart.data.labels.push("Regular");
                    };

                    if ("senior_questions" in result[key]) {
                        questionsChart.data.datasets[0]["data"].push(result[key]["senior_questions"]);
                        questionsChart.data.labels.push("Senior");
                    };


                    for (data in result[key]) {
                        if (data.endsWith("questions")) {
                            questionsChart.data.datasets[0]["backgroundColor"].push('#D3E4F3');
                        }
                    };
                    questionsChart.update();


                    // Save to jQuery object
                    $chartQuestionsCanvas.data('chart', questionsChart);
                };

                // Init chart
                if ($chartAnswersCanvas.length) {
                    initChartAnswers($chartAnswersCanvas);
                }

                if ($chartQuestionsCanvas.length) {
                    initChartQuestions($chartQuestionsCanvas);
                }

            };


        })();

        'use strict';
    };


};

});