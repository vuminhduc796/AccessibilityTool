import { createGlobalStyle } from "styled-components";
import {Button, Card} from "react-bootstrap";
import styled from "styled-components";

const GlobalStyle = createGlobalStyle`
    font-family: 'Inter';
    font-size: 16px;
    color: green;
`;

// text formating
export const Title = styled.h1`
    font-size: ${(props)=>props.theme.titleSize ? props.theme.titleSize  : ".9em"};
    color: ${(props) => props.theme.darkTextColor};
    font-weight: bolder;

`
export const SectionTitle = styled.h2`
    font-size: ${(props)=>props.theme.sectionHeadingSize ? props.theme.sectionHeadingSize  : ".9em"};
    color: ${(props) => props.theme.darkTextColor};
    font-weight: bold;
`
export const NormalText = styled.p`
    font-size: ${(props)=>props.theme.normalTextSize ? props.theme.normalTextSize  : ".9em"};
    color: ${(props) => props.theme.darkTextColor};

`

// buttons

export const PrimaryButton = styled(Button)`
    font-size: ${(props)=>props.theme.normalTextSize ? props.theme.normalTextSize  : ".9em"};
    font-weight: bold;
    height: ${(props) => props.theme.elementNormalHeight};
    color: white;
    background-color: ${(props) => props.theme.normalBlueColor};
    border-radius: 0px;
    border: none;

    &:hover {
    background-color: ${(props) => props.theme.normalBlueColor} !important;
    }
    &:focus {
    background-color: ${(props) => props.theme.normalBlueColor} !important;
    }
    &:visited {
    background-color: ${(props) => props.theme.normalBlueColor} !important;
    }
    &:active {
    background-color: ${(props) => props.theme.normalBlueColor} !important;
    }

`
export const SecondaryButton = styled(Button)`
    font-size: ${(props)=>props.theme.normalTextSize ? props.theme.normalTextSize  : ".9em"};
    font-weight: bold;
    height: ${(props) => props.theme.elementNormalHeight};
    color: ${(props) => props.theme.darkTextColor};
    background-color: ${(props) => props.theme.lightGreyColor};
    border-radius: 0px;
    border: none;

    &:hover {
    background-color: ${(props) => props.theme.lightGreyColor} !important;
    }
    &:focus {
    background-color: ${(props) => props.theme.lightGreyColor} !important;
    }
    &:visited {
    background-color: ${(props) => props.theme.lightGreyColor} !important;
    }
    &:active {
    background-color: ${(props) => props.theme.lightGreyColor} !important;
    }

`

// card

export const CarouselCard = styled(Card)`
    height: 220px;
    margin: 10px;
    background-color: ${(props) => props.theme.lightGreyColor};
    border: none;
    border-radius: 0px;
    padding: 0px;
`

export const CardImage = styled(Card.Img)`
    object-fit: fill;
    background-color: white;
    margin: 0px;
    padding: 0px;
    width: 100%;
    height: 170px;
   
`

export const CardTitle = styled(Card.Title)`
    text-align: left;
    margin-top: 20px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-weight: bold;
    color: ${(props) => props.theme.darkTextColor};
    margin: 5px;
`;

export const Hero = styled.div`
    text-align: left;
    padding: 20px;
    background-color: ${(props) => props.theme.backgroundBlueColor};
    color: ${(props) => props.theme.darkTextColor};

`;


export default GlobalStyle;
