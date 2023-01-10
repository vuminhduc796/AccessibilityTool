import * as React from "react"
import { useState } from "react";
import { useCallback } from "react";
import { Row, Col, Button } from "react-bootstrap";
import "./style.css";
import AcivityGraph from "../activityGraph/AcivityGraph";
import DetailPage from "../detailPage/DetailPage";
import Dropdown from 'react-bootstrap/Dropdown';
import { AppContext } from "../../context/Context";
import config from '../../data/config.json'
export const Home = () => {

    const [activityData, setCurrentActivity] = useState({
        id: 1,
        img: "72213.jpg",
        activity: "aactivity",
        nodeName: "node"
      });

      const [configs, setConfigs] = useState([]);
      const [gData, setData] = useState({nodes: [], links: []});

      const appNames = [];
      const modes = [];
      const devices = [];
      const configObject = {};
      let appName, mode, device;
      for (let i=0; i<config.configs.length; i++) {
          appName = config.configs[i].config.appName;
          mode = config.configs[i].config.mode;
          device = config.configs[i].config.device;
          if (!appNames.includes(appName)) {
              appNames.push(appName);
          }
          if (!modes.includes(mode)) {
              modes.push(mode);
          }
          if (!devices.includes(device)) {
              devices.push(device);
          }
  
          if (configObject[appName] === undefined) {
              configObject[appName] = {}
          }
          if (configObject[appName][device] === undefined) {
              configObject[appName][device] = [mode]
          }
          else {
              configObject[appName][device].push(mode);
          }
      }
  
      const [currentConfig, setCurrentConfig] = useState({
          appName: appNames[0],
          mode: modes[0],
          device: devices[0]
      })

    return(
        <AppContext.Provider value = {{
            "currentActivity": [activityData, setCurrentActivity], 
            
            "gData": [gData, setData],
            "configs": [configs, setConfigs],
            "currentConfig": [currentConfig, setCurrentConfig]
        }}
            >
        <div>
        <Row >
        <Col style={{padding:"0px", margin: "0px", backgroundColor:"#a7b099", border:"5px solid grey"}} > 
        <div >
            <Row style={{padding: "10px" , paddingLeft: "30px"
                    }}> 
            <Dropdown style={{width:"20%", padding: "0px"}}>
            <Dropdown.Toggle variant="secondary" id="dropdown-basic" 
                style={{width:"100%", fontSize: "20px"
                    }}>
                {currentConfig.appName}
            </Dropdown.Toggle>

            <Dropdown.Menu style={{width:"100%", fontSize: "20px"}} >
                {appNames.map((value) => <Dropdown.Item 
                    onClick={() => setCurrentConfig({...currentConfig,appName: value})}>
                    {value}</Dropdown.Item>)}
                
            </Dropdown.Menu>
            </Dropdown>
            <Dropdown style={{width:"20%"}}>
            <Dropdown.Toggle variant="secondary" id="dropdown-basic" 
                style={{width:"100%", fontSize: "20px"
                    }}>
                {currentConfig.device}
            </Dropdown.Toggle>

            <Dropdown.Menu style={{width:"100%", fontSize: "20px"}} >
                {devices.filter((value) => configObject[currentConfig.appName][value] !== undefined)
                .map((value) => <Dropdown.Item 
                    onClick={() => setCurrentConfig({...currentConfig,device: value})}>
                    {value}</Dropdown.Item>)}
                
            </Dropdown.Menu>
            </Dropdown>

            <Dropdown style={{width:"20%"}}>
            <Dropdown.Toggle variant="secondary" id="dropdown-basic" 
                style={{width:"100%", fontSize: "20px"
                    }}>
                {currentConfig.mode}
            </Dropdown.Toggle>

            <Dropdown.Menu style={{width:"100%", fontSize: "20px"}} >
                {modes.filter((value) => configObject[currentConfig.appName][currentConfig.device].includes(value) !== undefined)
                .map((value) => <Dropdown.Item 
                    onClick={() => setCurrentConfig({...currentConfig,mode: value})}>
                    {value}</Dropdown.Item>)}
                
            </Dropdown.Menu>
            </Dropdown>

            <Button style={{width:"10%", fontSize: "20px"}} variant="success"> Refresh</Button>    
            </Row>
     
        </div>
        <AcivityGraph/> 
        </Col>    
        <Col style={{padding:"10px", margin: "0px", backgroundColor:"#e5e8e1"}}>
        <Dropdown style={{width:"100%"}}>
            <Dropdown.Toggle variant="success" id="dropdown-basic" 
                style={{width:"100%", fontSize: "25px"
                    }}>
                {activityData.nodeName}
            </Dropdown.Toggle>

            <Dropdown.Menu style={{width:"100%", fontSize: "25px"}} >
                {gData.nodes.map((node) => <Dropdown.Item 
                    onClick={() => setCurrentActivity(node)}
                
                >{node.nodeName}</Dropdown.Item>)}
            </Dropdown.Menu>
            </Dropdown>        
            <DetailPage/>
        </Col>
        </Row>    

        </div>
        </AppContext.Provider>
    )
}
