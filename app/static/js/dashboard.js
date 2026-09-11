const cityselect=document.getElementById("city-select");
const pollutantselect=document.getElementById("pollutant-select");
const chartContainer=document.getElementById("chart-container");

const dateSelect = document.getElementById("date-select");
function populateDates(){
    const city=cityselect.value;
    fetch(`/get_dates?city=${city}`)
    .then(response=>response.json())
    .then(data=>{
        dateSelect.innerHTML='';
        data.dates.forEach(date => {
            const option = document.createElement('option');
            option.value = date;
            option.textContent = date;
            dateSelect.appendChild(option);
        });
    })
    .catch(error=>console.error('Error fetching dates:', error));
}
cityselect.addEventListener('change',populateDates);
populateDates(); // Initial population of dates when the page loads


function updateChart() {
    const city=cityselect.value;
    const pollutant=pollutantselect.value;
    fetch(`/get_data?city=${city}&pollutant=${pollutant}`)
    .then(response=>response.json())
    .then(data=>{
        const trace={
            x:data.dates,
            y:data.values,
            type:'scatter',
            mode:'lines',
            name:pollutant
        };
        const layout={
            title:`${pollutant} Levels in ${city}`,
            xaxis:{title:'Date'},
            yaxis:{title:`${pollutant} Level`}
        };
        
        Plotly.newPlot(chartContainer,[trace],layout);
    })
    .catch(error=>console.error('Error fetching data:', error));
}
cityselect.addEventListener('change',updateChart);
pollutantselect.addEventListener('change',updateChart);

const historicalButton=document.getElementById("predict-historical-button");
const historicalResult=document.getElementById("historical-result");
historicalButton.addEventListener('click',()=>{
    const city=cityselect.value;
    const date=dateSelect.value;

    fetch(`/predict_historical?city=${city}&date=${date}`)
    .then(response=>response.json())
    .then(data=>{
        historicalResult.innerHTML=`
                <p><strong>${data.city}</strong> on ${data.selected_date}</p>
                <p>Actual AQI: <strong>${data.actual_aqi}</strong></p>
                <p>Predicted AQI: <strong>${data.predicted_aqi}</strong></p>
                <p>Pollution Level: <strong>${data.pollution_level}</strong></p>
            `;
    })
    .catch(error=>console.error('Error fetching prediction:', error));
})  

const latestButton=document.getElementById("predict-latest-button");
const latestResult=document.getElementById("latest-result");
latestButton.addEventListener('click',()=>{
    const city=cityselect.value;
    fetch(`/predict_latest?city=${city}`)
    .then(response=>response.json())
    .then(data=>{
        latestResult.innerHTML=`
                <p><strong>${data.city}</strong> on ${data.selected_date}</p>
                <p>Predicted AQI: <strong>${data.predicted_aqi}</strong></p>
                <p>Pollution Level: <strong>${data.pollution_level}</strong></p>
            `;
    })
    .catch(error=>console.error('Error fetching prediction:', error));
})  
