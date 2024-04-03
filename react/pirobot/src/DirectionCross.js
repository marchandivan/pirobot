import Grid from "@mui/material/Grid";
import IconButton from '@mui/material/IconButton';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import DangerousIcon from '@mui/icons-material/Dangerous'
import NorthWestIcon from '@mui/icons-material/NorthWest'
import NorthEastIcon from '@mui/icons-material/NorthEast'
import SouthWestIcon from '@mui/icons-material/SouthWest'
import SouthEastIcon from '@mui/icons-material/SouthEast'
import React from 'react';

class DirectionCross extends React.Component {

    send_json = (json_data) => {
        this.state.ws.send(
            JSON.stringify(json_data)
        );
    }

    render() {
        return (
          <Grid container direction="column" spacing={2}>
            <Grid container item xs={4} spacing={2}>
                <Grid item xs={4}>
                  <IconButton onClick={this.props.move.bind(this.parent, 0, 100)} style={{"background-color": "grey"}}><NorthWestIcon/></IconButton>
                </Grid>
                <Grid item xs={4}>
                  <IconButton onClick={this.props.move.bind(this.parent, 100, 100)} style={{"background-color": "grey"}}><ArrowUpwardIcon/></IconButton>
                </Grid>
                <Grid item xs={4}>
                  <IconButton onClick={this.props.move.bind(this.parent, 100, 0)} style={{"background-color": "grey"}}><NorthEastIcon/></IconButton>
                </Grid>
            </Grid>

            <Grid container item xs={4} spacing={2}>
                <Grid item xs={4}>
                  <IconButton onClick={this.props.move.bind(this.parent, -100, 100)} style={{"background-color": "grey"}} ><ArrowBackIcon/></IconButton>
                </Grid>
                <Grid item xs={4}>
                  <IconButton onClick={this.props.stop} style={{"background-color": "grey"}} ><DangerousIcon/></IconButton>
                </Grid>
                <Grid item xs={4}>
                  <IconButton onClick={this.props.move.bind(this.parent, 100, -100)} style={{"background-color": "grey"}} ><ArrowForwardIcon/></IconButton>
                </Grid>
            </Grid>

            <Grid container item xs={4} spacing={2}>
                <Grid item xs={4}>
                  <IconButton onClick={this.props.move.bind(this.parent, -100, 0)} style={{"background-color": "grey"}} ><SouthWestIcon/></IconButton>
                </Grid>
                <Grid item xs={4}>
                  <IconButton onClick={this.props.move.bind(this.parent, -100, -100)} style={{"background-color": "grey"}} ><ArrowDownwardIcon/></IconButton>
                </Grid>
                <Grid item xs={4}>
                  <IconButton onClick={this.props.move.bind(this.parent, 0, -100)} style={{"background-color": "grey"}} ><SouthEastIcon/></IconButton>
                </Grid>
            </Grid>
          </Grid>
          )
    }
}

export default DirectionCross;
