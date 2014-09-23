using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class supr : MonoBehaviour {
	protected Vector3 V;
	protected Vector3[] prev = new Vector3[40];
	protected int init; protected float gx,gy;
	protected bool back;
	protected OVRCameraController occ = null;
	protected AudioSource ass = null;
	// Use this for initialization
	void Start () {
		init = 0;
		
	}
	// Update is called once per frame
	void Update () 
	{
		OVRCameraController[] CameraControllers;
		CameraControllers = FindObjectsOfType(typeof(OVRCameraController)) as OVRCameraController[];
		
		if(CameraControllers.Length == 0)
			Debug.LogWarning("OVRPlayerController: No OVRCameraController attached.");
		else if (CameraControllers.Length > 1)
			Debug.LogWarning("OVRPlayerController: More then 1 OVRCameraController attached.");
		else occ = CameraControllers[0];	
		if (init < 20) 
		{
			
			occ.GetCameraOrientationEulerAngles (ref prev[init++]);
		}
		else 
		{

			ass=GetComponent<AudioSource>();
			V = new Vector3 (0, 0, 0);
			occ.GetCameraOrientationEulerAngles (ref V);
			float dx=prev[0].x-V.x;
			print (dx+" "+(prev[0].x-V.x)+" "+(prev[0].z-V.z));
			float tot=Mathf.Abs(dx);
			if(float.IsNaN(tot)) tot=0;
			for(int i=0;i<19;i++) prev[i]=prev[i+1];
			init--;
			if(tot<15) return;
			float R=6;
			dx=R*Mathf.Sin(dx);
			//print (dx+" "+dy);
			if(back)
			{
				if(Mathf.Abs(dx)<2) return;
				dx=gx;
				back=false;
			}
			else
			{
				gx=-dx;
				back=true;
			}
			init=0; 
			this.transform.Translate(0,dx,0);
			ass.Play();
		}
	}
}

