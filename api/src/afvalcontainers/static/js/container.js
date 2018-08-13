(function() {
  // Create the connector object
  var myConnector = tableau.makeConnector();

  // Define the schema
  myConnector.getSchema = function(schemaCallback) {
    // Schema for magnitude and place data
    var container_cols = [{
      id: "id",
      dataType: tableau.dataTypeEnum.string
    },{
      id: "id_number",
      alias: "id number",
      dataType: tableau.dataTypeEnum.string
    }, {
      id: "waste_name",
      alias: "fractie",
      dataType: tableau.dataTypeEnum.string
    }, {
      id: "buurt_code",
      alias: "buurt_code",
      dataType: tableau.dataTypeEnum.string
    }, {
      id: "active",
      alias: "is active",
      dataType: tableau.dataTypeEnum.boolean
    }, {
      id: "address",
      alias: "address",
      dataType: tableau.dataTypeEnum.string
    }, {
      id: "lat",
      alias: "latitude",
      dataType: tableau.dataTypeEnum.float
    }, {
      id: "lon",
      alias: "longitude",
      dataType: tableau.dataTypeEnum.float
    }, {
      id: "volume",
      alias: "volume m3",
      dataType: tableau.dataTypeEnum.float
    }, {
      id: "site",
      alias: "site",
      dataType: tableau.dataTypeEnum.string
    }, {
      id: "placing_date",
      alias: "placing date",
      dataType: tableau.dataTypeEnum.date
    }];

    var containerTable = {
      id: "container",
      alias: "Container Data",
      columns: container_cols
      //endpoint: "containers"
    };

    // Schema for time and URL data
    // var time_url_cols = [{
    //   id: "id",
    //   dataType: tableau.dataTypeEnum.string
    // }, {
    //   id: "time",
    //   alias: "time",
    //   dataType: tableau.dataTypeEnum.date
    // }, {
    //   id: "url",
    //   alias: "url",
    //   dataType: tableau.dataTypeEnum.string
    // }];

    //var timeUrlTable = {
    //    id: "timeUrl",
    //    alias: "Time and URL Data",
    //    columns: time_url_cols
    //};

    schemaCallback([
      containerTable,
      //timeUrlTable
    ]);
  };

  // Download the data
  myConnector.getData = function(table, doneCallback) {
  // var dateObj = JSON.parse(tableau.connectionData),
  // dateString = "starttime=" + dateObj.startDate + "&endtime=" + dateObj.endDate,

  //var apiCall = "https://api.data.amsterdam.nl/afval/containers/";  // + dateString + "";
    var apiCall = "http://localhost:8889/localhost:8000/afval/containers/";  // + dateString + "";

    var params = {
      "format": "json",
      "detailed": 1,
      "page_size": 1000,
      "page": 1,
    };

    var page = 1;
    //var hasresults = [];
    var feat = [];
    var promises = [];

    function getPage(page) {

      params.page = page;

      promises.push($.getJSON(apiCall, params, function(resp) {

        feat = resp.results;

        var tableData = [];
        var i = 0;
        var row = [];
        var len = 0;

        if( feat === undefined || feat.length === 0 ){
          return;
        } else {
          if (table.tableInfo.id == "container") {
            for (i = 0, len = feat.length; i < len; i++) {
              row = {
                "id": feat[i].id,
                "id_number": feat[i].id_number,
                "address": feat[i].address,
                "waste_name": feat[i].waste_name,
                "active": feat[i].active,
                "volume": feat[i].container_type.volume,
                "placing_date": feat[i].placing_date
              };

              if(feat[i].well !== null) {
                row.lon = feat[i].well.geometrie.coordinates[0];
                row.lat = feat[i].well.geometrie.coordinates[1];
                row.buurt_code = feat[i].well.buurt_code;
                row.site = feat[i].well.site;
              }
              tableData.push(row);
            }
          }
          table.appendRows(tableData);
          console.log(table);
        }
      }));
    }

    do {
      getPage(page);
      page += 1;
      // get the next page.
      // as long as we get response continue loading!
      // I do not know how to do this with promises
    } while(page < 14);

    $.when.apply($, promises).then(function(){
      doneCallback();
    });
  };

  tableau.registerConnector(myConnector);

  // Create event listeners for when the user submits the form
  $(document).ready(function() {
    $("#submitButton").click(function() {
      tableau.connectionName = "Containers"; // This will be the data source name in Tableau
      tableau.submit(); // This sends the connector object to Tableau
    });
  });
})();
