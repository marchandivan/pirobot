import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import ArrowUpwardIcon from '@material-ui/icons/ArrowUpward';
import ArrowDownwardIcon from '@material-ui/icons/ArrowDownward';
import ArrowBackIcon from '@material-ui/icons/ArrowBack';
import ArrowForwardIcon from '@material-ui/icons/ArrowForward';
import FastForwardIcon from '@material-ui/icons/FastForward'
import FastRewindIcon from '@material-ui/icons/FastRewind'
import UTurnLeftIcon from '@mui/icons-material/UTurnLeft'
import UTurnRightIcon from '@mui/icons-material/UTurnRight'
import DangerousIcon from '@mui/icons-material/Dangerous';
import TurnSlightRightIcon from '@mui/icons-material/TurnSlightRight';
import TurnSlightLeftIcon from '@mui/icons-material/TurnSlightLeft';
import React from 'react';

class DirectionCross extends React.Component {

    render() {
        return (
          <Grid container>
            <Grid item xs={1}/>
            <Grid item xs={2}>
              <IconButton onClick={this.props.forward_left_callback}><FastRewindIcon/></IconButton>
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={this.props.forward_slight_left_callback}><ArrowBackIcon/></IconButton>
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={this.props.forward_callback}><ArrowUpwardIcon/></IconButton>
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={this.props.forward_slight_right_callback}><ArrowForwardIcon/></IconButton>
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={this.props.forward_right_callback}><FastForwardIcon/></IconButton>
            </Grid>
            <Grid item xs={1}/>

            <Grid item xs={1}/>
            <Grid item xs={2}>
              <IconButton onClick={this.props.uturn_left_callback}><UTurnLeftIcon/></IconButton>
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={this.props.slight_uturn_left_callback}><TurnSlightLeftIcon/></IconButton>
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={this.props.stop_callback}><DangerousIcon/></IconButton>
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={this.props.slight_uturn_right_callback}><TurnSlightRightIcon/></IconButton>
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={this.props.uturn_right_callback}><UTurnRightIcon/></IconButton>
            </Grid>
            <Grid item xs={1}/>


            <Grid item xs={1}/>
            <Grid item xs={2}>
              <IconButton onClick={this.props.backward_left_callback}><FastRewindIcon/></IconButton>
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={this.props.backward_slight_left_callback}><ArrowBackIcon/></IconButton>
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={this.props.backward_callback}><ArrowDownwardIcon/></IconButton>
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={this.props.backward_slight_right_callback}><ArrowForwardIcon/></IconButton>
            </Grid>
            <Grid item xs={2}>
              <IconButton onClick={this.props.backward_right_callback}><FastForwardIcon/></IconButton>
            </Grid>
            <Grid item xs={1}/>
          </Grid>
          )
    }
}

export default DirectionCross;
