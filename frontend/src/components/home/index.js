import * as React from "react"
import { useState } from "react";
import { useCallback } from "react";
import { Row, Col, Button } from "react-bootstrap";
import "./style.css";
import AcivityGraph from "../activityGraph/AcivityGraph";
import DetailPage from "../detailPage/DetailPage";
import Dropdown from 'react-bootstrap/Dropdown';
import { AppContext } from "../../context/Context";
export const Home = () => {

    const availableDevices = ["Vertical Phone", "Vertical Tablet", "Horizontal Phone", "Horizontal Tablet"]
    const modes = ["Light mode", "Dark mode"]
  
   

    const [currentConfig, setCurrentConfig] = useState({
        device: availableDevices[0],
        mode: modes[0]
    })

    const [nodeData, setCurrentNode] = useState({
        id: 1,
        img: "72213.jpg",
        activity: "aactivity"
      });

      const [configs, setConfigs] = useState([]);
      const [gData, setData] = useState({nodes: [], links: []});

    return(
        <AppContext.Provider value = {{
            "currentNode": [nodeData, setCurrentNode], 
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
                {currentConfig.device}
            </Dropdown.Toggle>

            <Dropdown.Menu style={{width:"100%", fontSize: "20px"}} >
                {availableDevices.map((value) => <Dropdown.Item 
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
                {modes.map((value) => <Dropdown.Item 
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
                {nodeData.activity}
            </Dropdown.Toggle>

            <Dropdown.Menu style={{width:"100%", fontSize: "25px"}} >
                {gData.nodes.map((node) => <Dropdown.Item 
                    onClick={() => setCurrentNode(node)}
                
                >{node.activity}</Dropdown.Item>)}
            </Dropdown.Menu>
            </Dropdown>        
            <DetailPage/>
        </Col>
        </Row>    

        </div>
        </AppContext.Provider>
    )
}
