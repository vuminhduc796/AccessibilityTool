import React from 'react'
import { useState } from "react";
import { useEffect } from 'react';
import { useCallback } from 'react';
import { useContext } from 'react';
import { useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import "./activityGraph.css"
import "bootstrap/dist/css/bootstrap.min.css";
import { useWindowSize } from '@react-hook/window-size';
import { AppContext } from '../../context/Context';

const AcivityGraph = React.memo(()  => {

    var data = useContext(AppContext);
    var [currentNode, setNode] = data["currentNode"]
    var [gData, setData] = data["gData"]
    var [currentConfig,setCurrentConfig] = data["currentConfig"]
    var [configs,setConfigs] = data["configs"]

    const [cacheData, setCacheData] =  useState({});
    const [cacheConfigs, setCacheConfigs] =  useState({});
    const [directory, setDirectory] =  useState("");
    
    const modesMapping = {"Light mode": "normal_light_mode", "Dark mode": "dark_mode"}
    const devicesMapping = {"Vertical Phone": "phone-vertical", "Vertical Tablet": "tablet-vertical", "Horizontal Phone": "phone-horizontal", "Horizontal Tablet": "tablet-horizontal"}

    const graphRef = useRef();

    const tryLoadData = () => {
      try {
       return require("../../data/config.json");
      } catch (err) {
       return null;
      }
    };

    useEffect(() => {
      
      const interval = setInterval(() => {

           
        
        var readData = tryLoadData()

        if (readData !== null){

          var dataConfigs = readData.configs;     

          if (dataConfigs !== cacheData || cacheConfigs !== currentConfig){


            setConfigs(dataConfigs)
          // use config to get directory
          var isFound = false;
          for(var currentConfigIndex = 0; currentConfigIndex < dataConfigs.length; currentConfigIndex ++){
            var dataConfig = dataConfigs[currentConfigIndex]
              if (dataConfig.config.device === currentConfig.device && dataConfig.config.mode ===  currentConfig.mode){
                isFound = true
                loadDataForGraph(dataConfig)
              }

            }
            setCacheData(dataConfigs);
            setCacheConfigs(currentConfig);
          }
        }
      }, 2000);
    
      return () => clearInterval(interval);
    }, [gData,directory,currentConfig,cacheConfigs,cacheData]);

    const loadDataForGraph = dataConfig => {
      var folderPath = dataConfig.config.appName + "/" + dataConfig.config.device + "/" + dataConfig.config.mode + "/" ;
      setDirectory(folderPath);
      // set data for node
        var newData = {nodes: [], links: []};
        var currentID = 0;
        for (var i = 0; i < dataConfig.config.activities.length; i++){
          var activityScreenshot = dataConfig.config.activities[i];
          var newNode = {
            id: currentID.toString(),
            img: activityScreenshot + ".png",
            activity: activityScreenshot,
            config: folderPath
          };
          if (currentID === 0) {
            setNode(newNode);
          }
          
          newData.nodes.push(newNode);
          currentID ++;
        }
        setData(newData);
    }
    const [width, height] = useWindowSize();
  return (
    <div >
<ForceGraph2D
      ref={graphRef}
      graphData={gData}
      maxZoom = {20}
      
      nodeCanvasObject={(node, ctx, globalScale) => { 
        var img = new Image(); 
        img.src = require( `../../data/${directory}activity_screenshots/${node.img}`)

        if(node.activity === currentNode.activity) {
          ctx.beginPath();
          ctx.fillStyle = "#fffb03";
          ctx.fillRect(node.x - 34, node.y - 69, 79, 139);
          ctx.stroke();
        }
        ctx.drawImage(img, node.x - 32, node.y - 67, 75, 135);

        }} 
        
        linkDirectionalArrowLength={5.5}
        linkDirectionalArrowRelPos={100}
        linkCurvature={0.25} 
        linkWidth={5}
        height= {height * 0.92}
        width= {width/1.7} 
        onNodeClick={ node => {setNode(node)}}
        onNodeDragEnd={node => {
          node.fx = node.x;
          node.fy = node.y;
          node.fz = node.z;
        }}
        nodePointerAreaPaint={(node, color, ctx) => {
          ctx.fillStyle = color;
          ctx.fillRect(node.x - 32, node.y - 67, 96, 135);
        }}
        />
    </div>

   
  )
});

export default AcivityGraph