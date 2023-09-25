/* eslint-disable no-restricted-syntax */
$.getJSON('data/jira.json', (data) => {
  let chart;

  // Yearly: Statistics
  $('div#yearly-statistics-table').html(data.yearly_statistics);

  // Monthly: Closed tickets
  const ctX = document.getElementById('monthly-closed-tickets-chart');
  const ctData = data.monthly_closed;
  const ctSets = [];

  for (const v of ctData.data.values()) {
    const set = {
      borderWidth: 1,
      data: v.data,
      label: v.label,
    };
    ctSets.push(set);
  }

  // eslint-disable-next-line no-undef
  chart = new Chart(ctX, {
    type: 'bar',
    data: {
      labels: ctData.labels,
      datasets: ctSets,
    },
    options: {
      plugins: {
        title: {
          display: true,
          text: 'Closed Tickets',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });

  // Monthly: Continued service overview
  const csoX = document.getElementById('monthly-continued-service-chart');
  const csoData = data.monthly_continued_service;
  const csoSets = [];

  for (const v of csoData.data.values()) {
    const set = {
      borderWidth: 1,
      data: v.data,
      label: v.label,
    };
    csoSets.push(set);
  }

  // eslint-disable-next-line no-undef
  chart = new Chart(csoX, {
    type: 'bar',
    data: {
      labels: csoData.labels,
      datasets: csoSets,
    },
    options: {
      plugins: {
        title: {
          display: true,
          text: 'Continued Service Overview',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });

  // Sprint: Core timings sd
  const scpX = document.getElementById('sprint-cycle-sd-chart');
  const scpData = data.sprint_core_timings_sd;
  const scpSets = [];

  for (const v of scpData.data.values()) {
    const set = {
      borderWidth: 1,
      data: v.data.mean,
      label: v.label,
      tension: 0.2,
    };
    scpSets.push(set);
  }

  // eslint-disable-next-line no-undef
  chart = new Chart(scpX, {
    type: 'line',
    data: {
      labels: scpData.labels,
      datasets: scpSets,
    },
    options: {
      plugins: {
        title: {
          display: true,
          text: 'Mean times (hours)',
        },
        tooltip: {
          callbacks: {
            afterLabel: (context) => [
              `Mean: ${scpData.data[context.datasetIndex].data.mean[context.dataIndex]}`,
              `Min: ${scpData.data[context.datasetIndex].data.minimum[context.dataIndex]}`,
              `Max: ${scpData.data[context.datasetIndex].data.maximum[context.dataIndex]}`,
              `Standard deviation: ${scpData.data[context.datasetIndex].data.stdev[context.dataIndex]}`,
              `# of tickets: ${scpData.data[context.datasetIndex].data.size[context.dataIndex]}`,
            ],
            label: (context) => context.dataset.label,
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });

  // Sprint: Core timings teams: resolution
  const sctX = document.getElementById('sprint-cycle-teams-chart');
  const sctData = data.sprint_core_timings_teams;
  const sctSets = [];

  for (const v of sctData.data.values()) {
    const set = {
      borderWidth: 1,
      data: v.data.mean,
      label: v.label,
      tension: 0.2,
    };
    sctSets.push(set);
  }

  // eslint-disable-next-line no-undef
  chart = new Chart(sctX, {
    type: 'line',
    data: {
      labels: sctData.labels,
      datasets: sctSets,
    },
    options: {
      plugins: {
        title: {
          display: true,
          text: 'Mean times (days)',
        },
        tooltip: {
          callbacks: {
            afterLabel: (context) => [
              `Mean: ${sctData.data[context.datasetIndex].data.mean[context.dataIndex]}`,
              `Min: ${sctData.data[context.datasetIndex].data.minimum[context.dataIndex]}`,
              `Max: ${sctData.data[context.datasetIndex].data.maximum[context.dataIndex]}`,
              `Standard deviation: ${sctData.data[context.datasetIndex].data.stdev[context.dataIndex]}`,
              `# of tickets: ${sctData.data[context.datasetIndex].data.size[context.dataIndex]}`,
            ],
            label: (context) => context.dataset.label,
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });

  // Yearly: Support live
  const svcLiveYDataList = data.yearly_support_live;

  // eslint-disable-next-line no-restricted-syntax
  for (const k of Object.keys(svcLiveYDataList)) {
    $('#yearly-support-live-charts').append(`<div class="col-3"><canvas id="yearly-support-live-${k}"></canvas></div>`);
    const svcLiveYX = document.getElementById(`yearly-support-live-${k}`);
    const svcLiveYData = svcLiveYDataList[k];
    const svcLiveYSets = [];

    for (const v of svcLiveYData.data.values()) {
      const set = {
        borderWidth: 1,
        data: v.data,
        label: v.label,
      };
      svcLiveYSets.push(set);
    }

    // eslint-disable-next-line no-undef
    chart = new Chart(svcLiveYX, {
      type: 'pie',
      data: {
        labels: svcLiveYData.labels,
        datasets: svcLiveYSets,
      },
      options: {
        plugins: {
          legend: {
            position: 'bottom',
          },
          title: {
            display: true,
            text: k,
          },
        },
      },
    });
  }

  // Monthly: Support services
  const svcSdMDataList = data.monthly_support_components;

  // eslint-disable-next-line no-restricted-syntax
  for (const k of Object.keys(svcSdMDataList)) {
    $('#monthly-support-services-charts').append(`<div class="col-6"><canvas id="monthly-support-services-chart-${k}"></canvas></div>`);
    const svcSdMX = document.getElementById(`monthly-support-services-chart-${k}`);
    const svcSdMData = svcSdMDataList[k];
    const svcSdMSets = [];

    for (const v of svcSdMData.data.values()) {
      const set = {
        borderWidth: 1,
        data: v.data,
        label: v.label,
      };
      svcSdMSets.push(set);
    }

    // eslint-disable-next-line no-undef
    chart = new Chart(svcSdMX, {
      type: 'bar',
      data: {
        labels: svcSdMData.labels,
        datasets: svcSdMSets,
      },
      options: {
        plugins: {
          legend: {
            position: 'left',
          },
          title: {
            display: true,
            text: k,
          },
        },
        scales: {
          x: {
            stacked: true,
          },
          y: {
            beginAtZero: true,
            stacked: true,
          },
        },
      },
    });
  }

  // Monthly: Teams services
  const svcTeamsMDataList = data.monthly_teams_components;

  // eslint-disable-next-line no-restricted-syntax
  for (const k of Object.keys(svcTeamsMDataList)) {
    $('#monthly-teams-services-charts').append(`<div class="col-6"><canvas id="monthly-teams-services-chart-${k}"></canvas></div>`);
    const svcTeamsMX = document.getElementById(`monthly-teams-services-chart-${k}`);
    const svcTeamsMData = svcTeamsMDataList[k];
    const svcTeamsMSets = [];

    for (const v of svcTeamsMData.data.values()) {
      const set = {
        borderWidth: 1,
        data: v.data,
        label: v.label,
      };
      svcTeamsMSets.push(set);
    }

    // eslint-disable-next-line no-undef, no-unused-vars
    chart = new Chart(svcTeamsMX, {
      type: 'bar',
      data: {
        labels: svcTeamsMData.labels,
        datasets: svcTeamsMSets,
      },
      options: {
        plugins: {
          legend: {
            position: 'left',
          },
          title: {
            display: true,
            text: k,
          },
        },
        scales: {
          x: {
            stacked: true,
          },
          y: {
            beginAtZero: true,
            stacked: true,
          },
        },
      },
    });
  }
});
