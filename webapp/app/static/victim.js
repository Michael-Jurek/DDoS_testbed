$(document).ready(function () {
  updateVictimData();

    $("#edit_victim_form").on("submit", function (e) {
      e.preventDefault();
      var formData = $(this).serialize();
  
      $.ajax({
        type: "POST",
        url: "/edit_victim",
        data: formData,
        success: function (data) {
          console.log(data);
          alert(data);
          updateVictimData();
        },
        error: function (xhr, status, error) {
          console.log("Error: " + error);
        },
      });
    });
    function updateVictimData() {
      $.getJSON('/victim_data', function(data) {
        if (data.victim_data) {
            $('.apache-version').text(data.victim_data.apache_version);
            $('.victim-cpu-cores').text(data.victim_data.cpu_cores);
            $('.victim-memory-limit').text(data.victim_data.memory_limit);
            $('.victim-memory-unit').text(data.victim_data.memory_unit);
        } else {
            $('#victim_data').html('<p>No victim data found.</p>');
        }
      });
    }
});

