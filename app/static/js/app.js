(function () {
  "use strict";

  function showAlert(type, message) {
    $("#alertBox")
      .removeClass("d-none alert-success alert-danger alert-warning alert-info")
      .addClass("alert-" + type)
      .text(message);
  }

  function hideAlert() {
    $("#alertBox").addClass("d-none").text("");
  }

  function renderUser(user) {
    const entries = Object.entries(user || {});
    const $details = $("#userDetails").empty();

    if (entries.length === 0) {
      $details.append('<dt class="col-sm-4">Status</dt><dd class="col-sm-8">Logged in</dd>');
      return;
    }

    entries.forEach(function ([key, value]) {
      const label = key.charAt(0).toUpperCase() + key.slice(1);
      const display = Array.isArray(value) ? value.join(", ") : String(value);
      $details.append('<dt class="col-sm-4"></dt><dd class="col-sm-8"></dd>');
      $details.find("dt:last").text(label);
      $details.find("dd:last").text(display);
    });
  }

  function setAuthenticated(authenticated, user) {
    if (authenticated) {
      $("#loginPanel").addClass("d-none");
      $("#sessionPanel").removeClass("d-none");
      $("#connectionStatus").removeClass("text-bg-light text-bg-secondary").addClass("text-bg-success").text("Logged in");
      renderUser(user);
    } else {
      $("#sessionPanel").addClass("d-none");
      $("#loginPanel").removeClass("d-none");
      $("#connectionStatus").removeClass("text-bg-success text-bg-light").addClass("text-bg-secondary").text("Logged out");
      renderUser({});
    }
  }

  function checkSession() {
    return $.getJSON("/api/auth/session")
      .done(function (data) {
        setAuthenticated(Boolean(data.authenticated), data.user || {});
      })
      .fail(function () {
        setAuthenticated(false, {});
        showAlert("warning", "Unable to read the current local session.");
      });
  }

  $(function () {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/service-worker.js").catch(function () {
        // Service worker registration failure should not block authentication.
      });
    }

    checkSession();

    $("#loginForm").on("submit", function (event) {
      event.preventDefault();
      hideAlert();

      const payload = {
        username: $("#username").val(),
        password: $("#password").val()
      };

      $("#loginButton").prop("disabled", true).text("Logging in...");

      $.ajax({
        url: "/api/auth/login",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify(payload)
      })
        .done(function (data) {
          setAuthenticated(true, data.user || {});
          $("#password").val("");
          showAlert("success", "Login completed successfully.");
        })
        .fail(function (xhr) {
          const message = xhr.responseJSON && xhr.responseJSON.error
            ? xhr.responseJSON.error
            : "Login failed.";
          setAuthenticated(false, {});
          showAlert("danger", message);
        })
        .always(function () {
          $("#loginButton").prop("disabled", false).text("Login");
        });
    });

    $("#logoutButton").on("click", function () {
      hideAlert();
      $("#logoutButton").prop("disabled", true).text("Logging out...");

      $.post("/api/auth/logout")
        .done(function () {
          setAuthenticated(false, {});
          showAlert("success", "Logout completed successfully.");
        })
        .fail(function () {
          showAlert("danger", "Logout failed.");
        })
        .always(function () {
          $("#logoutButton").prop("disabled", false).text("Logout");
        });
    });
  });
})();
