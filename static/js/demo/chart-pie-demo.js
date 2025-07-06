fetch('http://127.0.0.1:8000/api/presfora_data_pourcentage/')
  .then(response => response.json())
  .then(data => {

          var ctx = document.getElementById("myPieChart");
          var myPieChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
              labels: ["Solde", "Depense", "Prevision"],
              datasets: [{
                data: [data.pourcentage_solde, data.pourcentage_depense, data.pourcentage_prevision],
                backgroundColor: ['#4e73df', '#e74a3b', '#858796'],
                hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
                hoverBorderColor: "rgba(234, 236, 244, 1)",
              }],
            },
            options: {
              maintainAspectRatio: false,
              tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                borderColor: '#dddfeb',
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                caretPadding: 10,
              },
              legend: {
                display: false
              },
              cutoutPercentage: 80,
            },
          });

})
  .catch(error => console.error('Erreur lors de la récupération des données:', error));
