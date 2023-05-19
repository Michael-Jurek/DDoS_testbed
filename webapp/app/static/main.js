$(document).ready(function () {
  // Load bot count on page load
  updateBotCount();

  $("#generate_botnet_form").on("submit", function (e) {
    e.preventDefault();
    var formData = $(this).serialize();

    $.ajax({
      type: "POST",
      url: "/generate_botnet",
      data: formData,
      success: function (data) {
        console.log(data);
        alert(data);
        updateBotCount(); //Updating bot count after generating new ones
      },
      error: function (xhr, status, error) {
        console.log("Error: " + error);
      },
    });
  });

  $("#edit_botnet_form").on("submit", function (e) {
    e.preventDefault();
    var formData = $(this).serialize();

    $.ajax({
      type: "POST",
      url: "/edit_all_bots",
      data: formData,
      success: function (data) {
        console.log(data);
        alert(data);
        updateBotCount();
        reloadPage();
      },
      error: function (xhr, status, error) {
        console.log("Error: " + error);
      },
    });
  });

  $("#remove_botnet").click(function (e) {
    e.preventDefault();

    $.ajax({
      url: "/remove_botnet",
      success: function (data) {
        console.log(data);
        updateBotCount(); // updating bot count after removing
        reloadPage();
        
      },
      error: function (xhr, status, error) {
        console.log("Error: " + error);
      },
    });
  });

  $("#limit_network_form").on("submit", function (e)  {
    e.preventDefault();
    var formData = $(this).serialize();

    $.ajax({
      type: "POST",
      url: "/limit_network",
      data: formData,
      success: function (data) {
        console.log(data);
      },
      error: function (xhr, status, error) {
        console.log("Error: " + error);
      },
    });
  });

  
  $("#ping").on("click", function (e) {
    e.preventDefault();
    $.getJSON("/ping", function (data) {
      console.log(data);
    });
  });


  function updateBotCount() {
    $.getJSON('/show_bot_count', function(data) {
      $('#bot-count').text(data.show_bot_count);
    });
  }
  
  var del_buttons = document.querySelectorAll('.delete-bot'); 
  del_buttons.forEach(function(button) { 
    button.addEventListener('click', function(e) {
      var botData = button.getAttribute('data-id');
      console.log("hej")
      e.preventDefault();

      $.ajax({
        type: "POST",
        url: "/remove_bot",
        data: { "container_id": botData },
        success: function(response) {
          updateBotCount();
          reloadPage();
        },
        error: function(xhr, status, error) {
          console.log("Error: " + error);
        } }); }); });


  var buttons = document.querySelectorAll('.edit-bot'); 
  buttons.forEach(function(button) { 
    button.addEventListener('click', function() {

      var botData = button.getAttribute('data-id').split(",");
      var containerId = botData[0];
      var cpuCores = botData[1];
      var memoryLimit = botData[2];
      var memoryUnit = botData[3];
      var packetLoss = botData[4];
      var bandwidth = botData[5];
      var bandwidthUnit = botData[6];
      var delay = botData[7];

      const form = document.querySelector('#edit-bot-form');

      const containerIdInput = document.querySelector('#container_id');
      const cpuCoresInput = document.querySelector('#cpu_cores_per_container');
      const memoryLimitInput = document.querySelector('#memory_limit');
      const packetLossInput = document.querySelector('#packet_loss');
      const bandwidthInput = document.querySelector('#bandwidth');
      const delayInput = document.querySelector('#delay');
      let memoryUnitSelect = document.querySelector("#memory_unit");

      containerIdInput.value = containerId;
      cpuCoresInput.value = cpuCores;
      memoryLimitInput.value = memoryLimit;
      packetLossInput.value = packetLoss;
      bandwidthInput.value = bandwidth;
      delayInput.value = delay;
    });
  });

  $("#edit-bot-form").on("submit", function (e) {
    e.preventDefault();
    var formData = $(this).serialize();

    $.ajax({
      type: "POST",
      url: "/edit_bot",
      data: formData,
      success: function (data) {
        console.log(data);
        updateBotCount();
        reloadPage();
      },
      error: function (xhr, status, error) {
        console.log("Error: " + error);
      },
    });
  });

});

function reloadPage() {
  location.reload();
}
