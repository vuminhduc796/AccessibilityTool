import React from 'react'
import Dropdown from 'react-bootstrap/Dropdown';

const DropdownPicker = ({data}) => {

    
  return (
        <Dropdown style={{width:"100%"}}>
            <Dropdown.Toggle variant="success" id="dropdown-basic" style={{width:"100%", fontSize: "30px"}}>
                Activity Picker
            </Dropdown.Toggle>

            <Dropdown.Menu style={{width:"100%", fontSize: "30px"}}>
                <Dropdown.Item href="#/action-1">Action</Dropdown.Item>
                <Dropdown.Item href="#/action-2">Another action</Dropdown.Item>
                <Dropdown.Item href="#/action-3">Something else</Dropdown.Item>
            </Dropdown.Menu>
            </Dropdown>
  )
}

export default DropdownPicker