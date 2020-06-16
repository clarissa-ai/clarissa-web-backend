def get_routes():
    response_object = {}
    response_object["status"] = "success"
    response_object["message"] = "Successfully retrieved application routes."
    response_object["routes"] = {
      "/covid-19": "/survey/1",
      "/mental-health-screening": "/survey/2"
    }
    return response_object