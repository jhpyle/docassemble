/* global module:true */
module.exports = function (grunt) {
  'use strict';

  grunt.initConfig({

    pkg : grunt.file.readJSON( 'package.json' ),

    uglify : {

      options : {
        mangle : true
      },

      target : {
        files : {
          'dist/prettyCheckable.min.js' : ['dev/prettyCheckable.js']
        }
      }
    },

    compass : {

      dist : {
        options : {
          sassDir : 'dev',
          cssDir : 'dist',
          imagesDir : 'img',
          relativeAssets: true,
          environment: 'production'
        }
      }

    },

    watch : {
      dist : {
        files : [
          'dev/prettyCheckable.js',
          'dev/prettyCheckable.scss'
        ],

        tasks : [ 'default' ]
      }
    },

  });

  // Main tasks
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-compass');
  grunt.loadNpmTasks('grunt-contrib-watch');

  grunt.registerTask('default', [
    'compass',
    'uglify'
  ]);

  grunt.registerTask('w', ['watch']);

};