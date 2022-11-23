import React from 'react'
import { useContext } from 'react';
import { Row, Col } from "react-bootstrap";
import { useState } from "react";
import { AppContext } from '../../context/Context';

const DetailPage = () => {

  var data = useContext(AppContext);
  var [node, setNode] = data["currentNode"]

  const [google_report, setData] = useState("")
  if (node.config !== undefined){
    var cam_gb_img = require( `../../data/${node.config}ui_issue_cam/${node.activity}/cam_gb.jpg`);
    var cam_img = require( `../../data/${node.config}ui_issue_cam/${node.activity}/cam.jpg`);
    var gb_img = require( `../../data/${node.config}ui_issue_cam/${node.activity}/gb.jpg`);

    //var google_scanner_img = require( `/data/domain/phone-vertical/normal_light_mode/googleScanner/issues/au.com.domain.feature.home.HomeActivity/au.com.domain.feature.home.HomeActivity.png`);
    //var text_data = require( `/Users/vuminhduc796/Desktop/Research/Research Platform/accessibility-tool/src/data/domain/phone-vertical/normal_light_mode/googleScanner/issues/au.com.domain.feature.home.HomeActivity/au.com.domain.feature.home.HomeActivity.txt`);

  //   fetch(text_data)
  //       .then((r) => r.text())
  //       .then(text  => {
  //         setData(text);
  //       }) 
   }

  return (
    <div style={{width: "100%", paddingTop: "15px"}}>

        <h2 className="d-flex justify-content-between" style={{fontWeight: "bold"}}> Visual Issues</h2>
        <Row>
        <img src= {cam_img} style= {{width: '33%'}} alt = "cam scanner img"/>
        <img src= {cam_gb_img} style= {{width: '33%'}} alt = "cam gb scanner img"/>
        <img src= {gb_img} style= {{width: '33%'}} alt = "gb scanner img"/>
        </Row>
        <br/> 
        <h2 className="d-flex justify-content-between" style={{fontWeight: "bold"}}> Google Accessibility Scanner Report</h2>
        <Row>
        {/* <img src= {google_scanner_img} style= {{width: '33%'}} alt = "google scanner img"/> */}
        <textarea style= {{width: '66%'}} defaultValue={google_report}></textarea>
        </Row>
    </div>
  )
}

export default DetailPage 