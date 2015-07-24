"use strict";
var app = angular.module("VisaApp", []);

var colors = {
    ACCEPT: "#32A811",
    REJECT: "#CC4125",
    ON_ARRIVAL: "#E8E22A",
    OWN_COUNTRY: "#343AED",
    E_VISA: "#EF9CFB"
};

app.controller("VisaCtrl", function ($scope, $http) {
    $scope.selectedCountry = null;
    $scope.countries = {};
    $scope.visaStatus = {};
    $scope.legend = [
        { label: "Visa required", color: colors.REJECT },
        { label: "Visa-free", color: colors.ACCEPT },
        { label: "eVisa", color: colors.E_VISA },
        { label: "Visa on arrival", color: colors.ON_ARRIVAL },
        { label: $scope.selectedCountry, color: colors.OWN_COUNTRY },
    ];

    $scope.getCountryName = function (country) {
        if (country.indexOf(", ") >= 0) {
            var parts = country.split(", ");
            return parts[1] + " " + parts[0];
        } else {
            return country;
        }
    };

    $scope.getLegend = function () {
        var item;
        for (var i = 0; i < $scope.legend.length; i++) {
            item = $scope.legend[i];
            if (item.color === colors.OWN_COUNTRY) {
                item.label = $scope.selectedCountry;
            }
        }
        return $scope.legend;
    };

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
        listData.push([$scope.getCountryName($scope.selectedCountry), 0.25]);

        for (var country in data) {
            if (data[country].indexOf("Visa not required") >= 0 || data[country].indexOf("Visa free") >= 0 ||
                data[country].indexOf("Freedom of movement") >= 0) {
                smallList = [country, 1];
            } else if (data[country].indexOf("Visa required") >= 0) {
                smallList = [country, 0];
            } else if (data[country].indexOf("eVisa") >= 0 || data[country].indexOf("eVisitor") >= 0 || 
                    data[country].indexOf("e-Tourist Visa") >= 0 || data[country].indexOf("E-visa") >= 0 ||
                    data[country].indexOf("Online Visitor") >= 0 || data[country].indexOf("Electronic Travel Authority") >= 0 ||
                    data[country].indexOf("Online reciprocity fee") >= 0) {
                smallList = [country, 0.5];
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
                colors: [colors.REJECT, colors.OWN_COUNTRY, colors.E_VISA, colors.ON_ARRIVAL, colors.ACCEPT]
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
            var d = $scope.countries[country].replace(/ /g, "_");
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

    $scope.parseProblems = function (country) {
        if (country === null) {
            return false;
        }
        var keys = Object.keys($scope.visaStatus[country]);
        return keys.length < 2;
    };

    $scope.getCountries();
});
