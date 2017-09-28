angular.module("chatApp.controllers").controller("ChatCtrl", function($scope, ChatService) {
    $scope.messages = [];
    $scope.message = "";
    $scope.max = 140;
    $scope.controlForward = "1";
    $scope.controlForwardLeft = "2";
    $scope.controlForwardRight = "8";
    $scope.controlBackward = "5";
    $scope.controlBackwardLeft = "4";
    $scope.controlBackwardRight = "6";
    $scope.controlRight = "7";
    $scope.controlLeft = "3";
    $scope.controlStop = "0";
    $scope.controlManual = "manual";
    $scope.controlAuto = "auto";
    $scope.controlSemi = "semi";


    $scope.addMessage = function() {
        ChatService.send($scope.message);
        $scope.message = "";
    };

    $scope.addControlForward = function() {
        ChatService.send($scope.controlForward);
    };

    $scope.addControlForwardLeft = function() {
        ChatService.send($scope.controlForwardLeft);
    };

    $scope.addControlForwardRight = function() {
        ChatService.send($scope.controlForwardRight);
    };

    $scope.addControlBackward = function() {
        ChatService.send($scope.controlBackward);
    };

    $scope.addControlBackwardLeft = function() {
        ChatService.send($scope.controlBackwardLeft);
    };

    $scope.addControlBackwardRight = function() {
        ChatService.send($scope.controlBackwardRight);
    };

    $scope.addControlStop = function() {
        ChatService.send($scope.controlStop);
    };

    $scope.addControlManual = function() {
        ChatService.send($scope.controlManual);
        document.getElementById("manualBtn").disabled = true;
        document.getElementById("autoBtn").disabled = false;
        document.getElementById("semiBtn").disabled = false;
    };

    $scope.addControlAuto = function() {
        ChatService.send($scope.controlAuto);
        document.getElementById("manualBtn").disabled = false;
        document.getElementById("semiBtn").disabled = false;
        document.getElementById("autoBtn").disabled = true;
    };

    $scope.addControlSemiAuto = function() {
        ChatService.send($scope.controlSemi);
        document.getElementById("manualBtn").disabled = false;
        document.getElementById("semiBtn").disabled = true;
        document.getElementById("autoBtn").disabled = false;
    };

    $scope.addControlLeft = function() {
        ChatService.send($scope.controlLeft);
    };

    $scope.addControlRight = function() {
        ChatService.send($scope.controlRight);
    };

    ChatService.receive().then(null, null, function(message) {
        if (message.message !== "") {
            b = new Date(0);
            if (message.time.getTime() === b.getTime()) {
                var target = document.getElementById("target");
                target.src = 'data:image/jpg;base64,' + message.message;
            } else {
                var split = message.message.split(";");
                var target = document.getElementById("leftSensor");
                if (split[0] === 'nan')
                    target.innerHTML = "?";
                else
                    target.innerHTML = split[0] + ' cm';
                target = document.getElementById("frontLeftSensor");
                if (split[1] === 'nan')
                    target.innerHTML = "?";
                else
                    target.innerHTML = split[1] + ' cm';
                target = document.getElementById("frontSensor");
                if (split[2] === 'nan')
                    target.innerHTML = "?";
                else
                    target.innerHTML = split[2] + ' cm';
                target = document.getElementById("frontRightSensor");
                if (split[3] === 'nan')
                    target.innerHTML = "?";
                else
                    target.innerHTML = split[3] + ' cm';
                target = document.getElementById("rightSensor");
                if (split[4] === 'nan')
                    target.innerHTML = "?";
                else
                    target.innerHTML = split[4] + ' cm';

                target = document.getElementById("znak");
                if (split[5] === "Turn Right") {
                    target.src = "assets/turnRight.png";
                } else if (split[5] === "Turn Left") {
                    target.src = "assets/turnLeft.png";
                } else if (split[6] === "True") {
                    target.src = "assets/stop.png";
                } else {
                    target.src = "assets/empty.png";
                }
            }
        }
    });
});