import React from 'react';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import ImageListItemBar from '@mui/material/ImageListItemBar';
import IconButton from '@mui/material/IconButton';
import DownloadIcon from '@mui/icons-material/Download';
import Box from '@mui/material/Box';
import Tooltip from "@mui/material/Tooltip";
import { Link } from 'react-router-dom'
import HomeIcon from '@mui/icons-material/Home';

class PictureGallery extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            pictures: []
        }
    }

    componentDidMount() {
        let url_prefix = (window.location.port === "3000") ? "http://localhost:8080" : "";
        let url = url_prefix + '/api/v1/pictures';
        fetch(url)
            .then(response => response.json())
            .then(data => this.setState({pictures: data}))
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    get_picture_page = () => {
        let url_prefix = (window.location.port === "3000") ? "http://localhost:8080" : "";
        return (
            <ImageList cols={2} margin={10}>
              {this.state.pictures.map((picture_filename) => (
                <ImageListItem key={picture_filename}>
                  <img
                    srcSet={`${url_prefix}/api/v1/picture/${picture_filename}`}
                    src={`${url_prefix}/api/v1/picture/${picture_filename}`}
                    alt={picture_filename}
                    loading="lazy"
                  />
                  <ImageListItemBar
                    title={picture_filename}
                    position="top"
                    actionIcon={
                      <IconButton
                        sx={{ color: 'rgba(255, 255, 255, 0.54)' }}
                        aria-label={`info about ${picture_filename}`}
                        component="a" href={`${url_prefix}/api/v1/picture/${picture_filename}`} download
                      >
                       <DownloadIcon/>
                      </IconButton>
                    }
                  />
              </ImageListItem>
              ))}
            </ImageList>
        )
    }

    render() {
        document.body.style.overflow = "";
        return (
            <div className="App">
                <Box sx={{display: 'flex', width: 'fit-content', bgcolor: 'grey', margin: 1, border: (theme) => `1px solid ${theme.palette.divider}`, borderRadius: 1}}>
                    <Tooltip title="Home"><IconButton component={Link} to="/" ><HomeIcon/></IconButton></Tooltip>
                </Box>
                <p>Photo Gallery</p>
                    {this.get_picture_page()}
            </div>
        );
    }
}

export default PictureGallery;
