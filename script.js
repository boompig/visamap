"use strict";
var app = angular.module("VisaApp", []);

var colors = {
    ACCEPT: "#32A811",
    REJECT: "#CC4125",
    ON_ARRIVAL: "#E8E22A",
    OWN_COUNTRY: "#343AED"
};

app.controller("VisaCtrl", function ($scope, $http) {
    $scope.selectedCountry = null;
    $scope.countries = {};
    $scope.visaStatus = {};

    $scope.getStatus = function (country) {
        if (country === null) {
            return null;
        }
        if ($scope.visaStatus.hasOwnProperty(country)) {
            return $scope.visaStatus[country];
        }
    };

    $scope.drawOnChart = function () {
        var data = $scope.getStatus($scope.selectedCountry);
        var listData = [], smallList;

        // add title
        listData.push(["Country", "Visa Requirement"]);
        listData.push([$scope.selectedCountry, 0.25]);

        for (var country in data) {
            if (data[country].indexOf("Visa not required") >= 0 || data[country].indexOf("Visa free") >= 0) {
                smallList = [country, 1];
            } else if (data[country].indexOf("Visa required") >= 0) {
                smallList = [country, 0];
            } else if (data[country].indexOf("Visa on arrival") >= 0) {
                smallList = [country, 0.75];
            } else {
                smallList = null;
            }

            if (smallList) {
                listData.push(smallList);
            }
        }
        console.log(listData);
        var dataTable = google.visualization.arrayToDataTable(listData);

        // now that we have chart data
        var options = {
            colorAxis: {
                colors: [colors.REJECT, colors.OWN_COUNTRY, "#000000", colors.ON_ARRIVAL, colors.ACCEPT]
            }
        };
        var chart = new google.visualization.GeoChart(document.getElementById("map-container"));
        chart.draw(dataTable, options);
    };

    $scope.selectCountry = function (country) {
        if ($scope.visaStatus.hasOwnProperty(country)) {
            $scope.selectedCountry = country;

            $scope.drawOnChart ();
        } else {
            var d = $scope.countries[country].replace(" ", "_");
            $http.get("json/" + d + ".json").success(function (response) {
                console.log(response);
                $scope.visaStatus[country] = response;
                $scope.selectedCountry = country;

                $scope.drawOnChart ();
            });
        }
    };

    $scope.getCountries = function () {
        $http.get("json/countries.json").success(function (response) {
            $scope.countries = response;
        });
    };

    $scope.getCountries();
});
