import Grid from '@material-ui/core/Grid';
import React from 'react';
import IconButton from "@material-ui/core/IconButton";
import BackspaceIcon from '@mui/icons-material/Backspace';
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';
import BrightnessHighIcon from '@mui/icons-material/BrightnessHigh';
import BrightnessMediumIcon from '@mui/icons-material/BrightnessMedium';
import BrightnessLowIcon from '@mui/icons-material/BrightnessLow';
import FavoriteIcon from '@mui/icons-material/Favorite';
import SentimentSatisfiedIcon from '@mui/icons-material/SentimentSatisfied';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import SvgIcon from '@mui/material/SvgIcon';
import Divider from '@material-ui/core/Divider';

class LightControl extends React.Component {

    render() {
        if (this.props.hide) {
            return null;
        }
        return (
            <Grid container justifyContent="center" alignItems="center">
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <p>
                        Screen
                    </p>
                </Grid>
                <Grid item xl={1} md={1} sm={1} xs={1}/>
                <Grid item xl={2} md={2} sm={2} xs={2}>
                    <IconButton onClick={this.props.resetLcdScreen}><BackspaceIcon/></IconButton>
                </Grid>
                <Grid item xl={2} md={2} sm={2} xs={2}>
                    <IconButton onClick={this.props.updateLcdBrightness.bind(this, 0)}><PowerSettingsNewIcon/></IconButton>
                </Grid>
                <Grid item xl={2} md={2} sm={2} xs={2}>
                    <IconButton onClick={this.props.updateLcdBrightness.bind(this, 20)}><BrightnessLowIcon/></IconButton>
                </Grid>
                <Grid item xl={2} md={2} sm={2} xs={2}>
                    <IconButton onClick={this.props.updateLcdBrightness.bind(this, 60)}><BrightnessMediumIcon/></IconButton>
                </Grid>
                <Grid item xl={2} md={2} sm={2} xs={2}>
                    <IconButton onClick={this.props.updateLcdBrightness.bind(this, 100)}><BrightnessHighIcon/></IconButton>
                </Grid>
                <Grid item xl={1} md={1} sm={1} xs={1}/>
                <Grid item xl={2} md={2} sm={2} xs={2}>
                    <IconButton onClick={this.props.setLcdPicture.bind(this, "heart")}><FavoriteIcon/></IconButton>
                </Grid>
                <Grid item xl={2} md={2} sm={2} xs={2}>
                    <IconButton onClick={this.props.setLcdPicture.bind(this, "smile")}><SentimentSatisfiedIcon/></IconButton>
                </Grid>
                <Grid item xl={2} md={2} sm={2} xs={2}>
                    <IconButton onClick={this.props.setLcdPicture.bind(this, "sad")}><SentimentDissatisfiedIcon/></IconButton>
                </Grid>
                <Grid item xl={2} md={2} sm={2} xs={2}>
                    <IconButton onClick={this.props.setLcdPicture.bind(this, "laugh")}>
                        <SvgIcon>
                            <path fill="currentColor" d="M6 11V12.5H7.5V14H9V11M12.5 6H11V9H14V7.5H12.5M9.8 17A5.5 5.5 0 0 0 17 9.8M6.34 6.34A8 8 0 0 1 15.08 4.62A4.11 4.11 0 0 1 15.73 2.72A10 10 0 0 0 2.73 15.72A4.11 4.11 0 0 1 4.63 15.07A8 8 0 0 1 6.34 6.34M17.66 17.66A8 8 0 0 1 8.92 19.38A4.11 4.11 0 0 1 8.27 21.28A10 10 0 0 0 21.27 8.28A4.11 4.11 0 0 1 19.37 8.93A8 8 0 0 1 17.66 17.66M6 11V12.5H7.5V14H9V11M9.8 17A5.5 5.5 0 0 0 17 9.8M12.5 6H11V9H14V7.5H12.5M6 11V12.5H7.5V14H9V11M12.5 6H11V9H14V7.5H12.5M9.8 17A5.5 5.5 0 0 0 17 9.8M4.93 21A2 2 0 0 1 2.93 19A2 2 0 0 1 4.93 17H6.93V19A2 2 0 0 1 4.93 21.07M19.07 2.93A2 2 0 0 1 21.07 4.93A2 2 0 0 1 19.07 6.93H17.07V4.93A2 2 0 0 1 19.07 2.93Z" />
                        </SvgIcon>
                    </IconButton>
                </Grid>
                <Grid item xl={2} md={2} sm={2} xs={2}>
                    <IconButton onClick={this.props.setLcdPicture.bind(this, "caterpillar")}>
                        <SvgIcon viewBox="0 0 44 33">
                            <ellipse ry="4.37259" rx="4.08742" id="svg_1" cy="28.52021" cx="32.48364" stroke="#555" fill="#555"/>
                            <ellipse ry="4.37259" rx="4.08742" id="svg_2" cy="28.52021" cx="32.48364" stroke="#555" fill="#555"/>
                            <ellipse ry="4.37259" rx="4.08742" id="svg_6" cy="28.52021" cx="27.16049" stroke="#555" fill="#555"/>
                            <ellipse ry="4.37259" rx="4.08742" id="svg_7" cy="28.52021" cx="22.02746" stroke="#555" fill="#555"/>
                            <ellipse ry="4.37259" rx="4.08742" id="svg_8" cy="28.13998" cx="16.70431" stroke="#555" fill="#555"/>
                            <ellipse ry="4.37259" rx="4.08742" id="svg_9" cy="23.7674" cx="12.14161" stroke="#555" fill="#555"/>
                            <ellipse ry="4.37259" rx="4.08742" id="svg_10" cy="18.63436" cx="10.24049" stroke="#555" fill="#555"/>
                            <ellipse ry="6.9391" rx="6.84405" id="svg_11" cy="10.93481" cx="9.76521" stroke="#555" fill="#555"/>
                            <ellipse ry="1.0" rx="1.0" id="svg_19" cy="9.12874" cx="7.57891" stroke="#999" fill="#999"/>
                            <ellipse ry="1.0" rx="1.0" id="svg_20" cy="9.12874" cx="13.28229" stroke="#999" fill="#999"/>
                            <path id="svg_24" d="m6.24932,13.35321c4.04581,1.86889 4.17225,2.02145 7.45947,-0.1907" opacity="NaN" stroke="none" fill="#999"/>
                            <path id="svg_28" d="m13.40934,5.28033" opacity="NaN" stroke="#000" fill="#555"/>
                            <path id="svg_30" d="m13.16553,4.79272c1.95045,-4.38851 3.65709,-5.85135 5.24183,-4.0228" opacity="NaN" stroke="#555" fill="none"/>
                            <path id="svg_31" d="m5.97325,5.52414c-2.19426,-4.26661 -4.0228,-5.48564 -5.97325,-3.53519" opacity="NaN" stroke="#555" fill="none"/>
                        </SvgIcon>
                    </IconButton>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <p>
                        Mood
                    </p>
                </Grid>
                <Grid item xl={1} md={1} sm={1} xs={1}/>
                <Grid item xl={9} md={9} sm={9} xs={9}>
                  <Select
                    fullWidth
                    value={this.props.mood}
                    label="Age"
                    onChange={this.props.updateMood}
                  >
                    {
                        this.props.moods.map((mood) =>
                        <MenuItem key={mood} value={mood}>{mood}</MenuItem>)
                    }
                  </Select>
                </Grid>
                <Grid item xl={12} md={12} sm={12} xs={12}>
                    <p/>
                    <Divider/>
                </Grid>
            </Grid>
        )
    }
}

export default LightControl;
